import { Card } from "@/components/ui/card";

export default function TermsPage() {
  return (
    <Card className="p-6">
      <h1 className="text-2xl font-extrabold">Terms</h1>
      <p className="mt-2 text-sm text-muted-foreground">Document de démonstration.</p>
      <div className="mt-5 h-px bg-border" />
      <p className="mt-4 text-sm text-muted-foreground">
        Cette application est un projet pédagogique. Aucun service commercial réel n’est fourni via ce dépôt.
      </p>
    </Card>
  );
}

