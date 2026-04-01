import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="grid gap-6 md:grid-cols-2 md:items-center">
        <div className="space-y-4">
          <h1 className="text-4xl font-extrabold tracking-tight md:text-5xl">
            Un vrai SaaS moderne pour gérer vos cours, calendriers et messages.
          </h1>
          <p className="text-muted-foreground text-lg">
            Landing, pricing, onboarding… et une app “workspace” derrière login. Design premium, rapide, clair.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link href="/pricing">
              <Button>Voir les plans</Button>
            </Link>
            <Link href="/features">
              <Button variant="ghost">Découvrir</Button>
            </Link>
          </div>
          <div className="text-muted-foreground text-sm">
            Démo pédagogique. Pas de paiement réel.
          </div>
        </div>

        <Card className="p-5">
          <div className="grid gap-3 md:grid-cols-2">
            <Card className="p-4 shadow-none">
              <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Dashboard</div>
              <div className="mt-2 text-2xl font-extrabold">KPIs</div>
              <div className="mt-1 text-sm text-muted-foreground">Cours, inbox, notes.</div>
            </Card>
            <Card className="p-4 shadow-none">
              <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Workspace</div>
              <div className="mt-2 text-2xl font-extrabold">SaaS</div>
              <div className="mt-1 text-sm text-muted-foreground">Courses, calendar, org.</div>
            </Card>
            <Card className="p-4 shadow-none">
              <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Security</div>
              <div className="mt-2 text-2xl font-extrabold">Modes</div>
              <div className="mt-1 text-sm text-muted-foreground">vuln / secure.</div>
            </Card>
            <Card className="p-4 shadow-none">
              <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Deploy</div>
              <div className="mt-2 text-2xl font-extrabold">Vercel</div>
              <div className="mt-1 text-sm text-muted-foreground">Next.js natif.</div>
            </Card>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card className="p-5">
          <div className="text-sm font-bold">Onboarding simple</div>
          <p className="mt-2 text-sm text-muted-foreground">Un parcours clair : landing → pricing → login.</p>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-bold">UI premium</div>
          <p className="mt-2 text-sm text-muted-foreground">Typo, spacing, cards, gradients, micro-interactions.</p>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-bold">Pages “produit”</div>
          <p className="mt-2 text-sm text-muted-foreground">Features, pricing, legal, login.</p>
        </Card>
      </section>
    </div>
  );
}

