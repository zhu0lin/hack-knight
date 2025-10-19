// app/voiceAgent.ts
// Singleton WebRTC session + strong end() + exported status helpers.

type VoiceSession = { end: () => void };

function getBackendUrl(): string {
  return process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
}

// ---------- Singleton state ----------
let starting = false;
let ending = false;
let currentSession: any = null;
let currentMic: MediaStream | null = null;
let currentAudio: HTMLAudioElement | null = null;

function getAudioEl(): HTMLAudioElement {
  const id = "elevenlabs-voice-audio";
  let el = document.getElementById(id) as HTMLAudioElement | null;
  if (!el) {
    el = document.createElement("audio");
    el.id = id;
    el.autoplay = true;
    // @ts-ignore
    el.playsInline = true;
    el.style.display = "none";
    document.body.appendChild(el);
  }
  return el;
}

async function endSessionInternal() {
  if (ending) return;
  ending = true;

  try { currentMic?.getTracks().forEach(t => t.stop()); } catch {}
  currentMic = null;

  try {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.muted = true;
      // @ts-ignore
      currentAudio.srcObject = null;
    }
  } catch {}

  try { currentSession?.end?.(); } catch {}
  try { currentSession?.disconnect?.(); } catch {}
  try { currentSession?.close?.(); } catch {}
  try { currentSession?.leave?.(); } catch {}
  try { currentSession?.destroy?.(); } catch {}

  try {
    const pc = currentSession?.peerConnection || currentSession?.pc || currentSession?.connection;
    pc?.getSenders?.().forEach((s: RTCRtpSender) => { try { s.track?.stop(); } catch {} });
    pc?.getReceivers?.().forEach((r: RTCRtpReceiver) => { try { (r.track as any)?.stop?.(); } catch {} });
    pc?.close?.();
  } catch {}

  currentSession = null;
  ending = false;
}

export async function endActiveVoiceSession() {
  await endSessionInternal();
}

export function isVoiceLive(): boolean {
  return !!currentSession || starting; // treat “starting” as live to keep End enabled
}

export async function startVoiceSession(
  agentInstructions = "You are a friendly nutrition coach. Ask one clarifying question and include macros."
): Promise<VoiceSession> {
  // Ensure no overlap
  if (starting || currentSession) {
    await endSessionInternal();
  }

  starting = true;
  try {
    const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
    currentMic = mic;

    const r = await fetch(`${getBackendUrl()}/voice/realtime/token`, { method: "POST" });
    if (!r.ok) throw new Error(`token fetch failed: ${r.status}`);
    const { token, agent_id } = await r.json();

    const mod: any = await import("@elevenlabs/client");
    const WebRTCConnection = (mod as any).WebRTCConnection;
    if (!WebRTCConnection?.create) throw new Error("WebRTCConnection.create not available");

    const opts: any = { apiKey: token };
    if (agent_id) opts.agentId = agent_id; else opts.instructions = agentInstructions;

    const session = await WebRTCConnection.create(opts);
    currentSession = session;

    if (typeof session.sendUserMedia !== "function") {
      throw new Error("WebRTC session missing sendUserMedia");
    }
    await session.sendUserMedia(mic);

    const remote = await session.getRemoteAudioStream?.();
    if (!remote) throw new Error("No remote audio stream");
    const audio = getAudioEl();
    // @ts-ignore
    audio.srcObject = remote;
    audio.muted = false;
    await audio.play().catch(() => {});
    currentAudio = audio;

    const end = () => { void endSessionInternal(); };
    window.addEventListener("beforeunload", end, { once: true });

    return { end };
  } finally {
    starting = false;
  }
}
