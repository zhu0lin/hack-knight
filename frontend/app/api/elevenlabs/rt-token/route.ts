// frontend/app/api/elevenlabs/rt-token/route.ts
import { NextResponse } from "next/server";

export const GET = async () => {
  try {
    const apiKey = process.env.ELEVENLABS_API_KEY!;
    if (!apiKey) {
      return NextResponse.json(
        { error: "Missing ELEVENLABS_API_KEY" },
        { status: 500 }
      );
    }

    // Ask ElevenLabs for an ephemeral realtime token
    const r = await fetch("https://api.elevenlabs.io/v1/realtime/token", {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // keep as empty object for compatibility
    });

    if (!r.ok) {
      const text = await r.text();
      return NextResponse.json(
        { error: `Token create failed: ${text}` },
        { status: 500 }
      );
    }

    const json = await r.json(); // usually { token, expires_at }
    return NextResponse.json(json);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
};
