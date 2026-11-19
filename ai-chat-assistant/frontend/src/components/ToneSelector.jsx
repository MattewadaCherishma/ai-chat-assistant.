import { SlidersHorizontal } from "lucide-react";

const tones = [
  { value: "professional", label: "Professional" },
  { value: "casual", label: "Casual" },
  { value: "concise", label: "Concise" },
];

export default function ToneSelector({ tone, onChange, disabled }) {
  return <label className="tone-control"><SlidersHorizontal size={15}/><span>Tone</span>
    <select value={tone} onChange={e => onChange(e.target.value)} disabled={disabled}>
      {tones.map(t => <option value={t.value} key={t.value}>{t.label}</option>)}
    </select>
  </label>;
}
