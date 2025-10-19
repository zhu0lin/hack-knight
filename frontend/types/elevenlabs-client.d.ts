// types/elevenlabs-client.d.ts
declare module "@elevenlabs/client" {
  // default export style
  const ElevenLabs: any;
  export default ElevenLabs;

  // also allow named style (just in case)
  export function createClient(opts: any): any;
}
