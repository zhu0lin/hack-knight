import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const text = new URL(req.url).searchParams.get("text") || "Hello from ElevenLabs!";
  const voiceId = process.env.ELEVENLABS_VOICE_ID!;
  const apiKey = process.env.ELEVENLABS_API_KEY!;

  try {
    const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
      },
      body: JSON.stringify({
        text,
        model_id: "eleven_multilingual_v2",
        voice_settings: {
          stability: 0.35,
          similarity_boost: 0.85,
          style: 0.2,
          use_speaker_boost: true,
        },
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      return new NextResponse("Error: " + err, { status: 500 });
    }

    return new NextResponse(res.body as ReadableStream, {
      headers: { "Content-Type": "audio/mpeg", "Cache-Control": "no-store" },
    });
  } catch (e: any) {
    return new NextResponse("Fetch failed: " + e.message, { status: 500 });
  }
}
