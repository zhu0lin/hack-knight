import VoiceWidget from "../components/VoiceWidget";

export default function VoiceTestPage() {
  return (
    <main style={{ padding: 20 }}>
      <h1>Voice Agent Test</h1>
      <p>Click Start, allow mic, speak; click End to stop.</p>
      <VoiceWidget />
    </main>
  );
}
