import { Card } from "@/components/ui/card";

export default function PrivacyPage() {
  return (
    <Card className="p-6">
      <h1 className="text-2xl font-extrabold">Privacy</h1>
      <p className="mt-2 text-sm text-muted-foreground">Document de démonstration.</p>
      <div className="mt-5 h-px bg-border" />
      <p className="mt-4 text-sm text-muted-foreground">
        La partie “workspace” du projet utilise SQLite. En déploiement serverless, la base peut être éphémère.
      </p>
    </Card>
  );
}

