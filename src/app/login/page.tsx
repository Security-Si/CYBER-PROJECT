import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-2 md:items-start">
      <Card className="p-6">
        <h1 className="text-2xl font-extrabold">Log in</h1>
        <p className="mt-2 text-sm text-muted-foreground">Connectez-vous à votre workspace.</p>

        <form className="mt-6 space-y-3">
          <div>
            <label className="text-sm font-bold" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              className="mt-2 h-11 w-full rounded-xl border bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-blue-600/30"
              placeholder="student"
            />
          </div>
          <div>
            <label className="text-sm font-bold" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="mt-2 h-11 w-full rounded-xl border bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-blue-600/30"
              placeholder="••••••••"
            />
          </div>
          <Button type="button" className="w-full">
            Sign in
          </Button>
          <div className="text-xs text-muted-foreground">
            Cette page est une vitrine Next.js. L’auth métier reste côté Flask (workspace).
          </div>
        </form>
      </Card>

      <div className="space-y-4">
        <Card className="p-6">
          <div className="text-sm font-bold">Demo SaaS</div>
          <p className="mt-2 text-sm text-muted-foreground">
            Landing + pricing + login ultra modernes. Pour conserver les vulnérabilités et la logique, l’app Flask reste le backend actuel.
          </p>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-bold">Next steps</div>
          <p className="mt-2 text-sm text-muted-foreground">
            On peut brancher ce login au backend Flask (API) si tu veux une authentification réelle côté Next.
          </p>
        </Card>
      </div>
    </div>
  );
}

