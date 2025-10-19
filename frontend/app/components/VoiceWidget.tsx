// app/components/VoiceWidget.tsx
"use client";
import React, { useEffect, useState } from "react";
import { startVoiceSession, endActiveVoiceSession } from "../voiceAgent";

export default function VoiceWidget() {
  const [busy, setBusy] = useState(false);
  const [session, setSession] = useState<{ end: () => void } | null>(null);

  async function onStart() {
    if (busy) return;
    setBusy(true);
    try {
      await endActiveVoiceSession();          // pre-clean
      const handle = await startVoiceSession();
      setSession(handle);                     // we’re live
    } catch (e) {
      console.debug("[voice] start non-fatal:", e);
      setSession(null);
    } finally {
      setBusy(false);
    }
  }

  async function endNow() {
    try {
      session?.end();                         // end via session handle
      await endActiveVoiceSession();          // hard end (singleton)
    } catch (e) {
      console.debug("[voice] end non-fatal:", e);
    } finally {
      setSession(null);                       // immediately re-enable Start
    }
  }

  // Escape key as emergency hang-up
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") endNow(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [session]);

  return (
    <div style={{ display: "flex", gap: 12, alignItems: "center", position: "relative", zIndex: 9999 }}>
      <button onClick={onStart} disabled={busy || !!session}>Start Voice</button>
      {/* Always clickable. Use onMouseDown so it fires even while focus/DOM is mid-change. */}
      <button
        onMouseDown={endNow}
        onClick={endNow}
        style={{ cursor: "pointer" }}
      >
        End Voice
      </button>
      {busy ? <span>Starting…</span> : session ? <span>🎙️ Live</span> : null}
    </div>
  );
}
