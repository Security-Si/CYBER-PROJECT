import { Card } from "@/components/ui/card";

const items = [
  { title: "Dashboard", desc: "KPIs, shortcuts, upcoming." },
  { title: "Courses", desc: "Cours + annonces, navigation rapide." },
  { title: "Calendar", desc: "Agenda + notes personnelles." },
  { title: "Inbox", desc: "Messages et détail." },
  { title: "Organization", desc: "Workspace d’équipe (démo)." },
  { title: "Billing", desc: "Plans et factures (démo)." }
];

export default function FeaturesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight">Features</h1>
        <p className="mt-2 text-muted-foreground">Tout ce qu’il faut pour une expérience SaaS crédible.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {items.map((it) => (
          <Card key={it.title} className="p-5">
            <div className="font-bold">{it.title}</div>
            <div className="mt-2 text-sm text-muted-foreground">{it.desc}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}

