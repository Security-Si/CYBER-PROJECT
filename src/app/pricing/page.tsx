import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const plans = [
  { name: "Starter", price: "€0", tag: "Pour tester", features: ["1 workspace", "Courses + Calendar", "Community support"] },
  { name: "Pro", price: "€19", tag: "Recommandé", features: ["Organization", "Inbox + search", "Billing (démo)"] },
  { name: "Enterprise", price: "Sur devis", tag: "Écoles", features: ["SSO (démo)", "Audit", "SLA"] }
];

export default function PricingPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Pricing</h1>
          <p className="mt-2 text-muted-foreground">Des plans simples. Paiement non implémenté (démo).</p>
        </div>
        <Link href="/login">
          <Button>Get started</Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((p) => (
          <Card key={p.name} className="p-6">
            <div className="flex items-center justify-between">
              <div className="text-lg font-extrabold">{p.name}</div>
              <div className="rounded-full border px-3 py-1 text-xs font-bold text-muted-foreground">{p.tag}</div>
            </div>
            <div className="mt-4 text-4xl font-extrabold">{p.price}</div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              {p.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-600" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <div className="mt-6">
              <Link href="/login">
                <Button className="w-full">{p.name === "Pro" ? "Choisir Pro" : "Commencer"}</Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

