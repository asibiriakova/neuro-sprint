This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Auth setup (Supabase)

Signup, login, logout, and session handling use Supabase Auth via
`@supabase/ssr` (see `lib/supabase/`, `proxy.ts`, and `app/{login,signup,dashboard}`).
This app does not create a Supabase project or store real credentials —
you need to provide your own:

1. Create a project at [supabase.com/dashboard](https://supabase.com/dashboard)
   (or reuse an existing one).
2. Copy `.env.example` to `.env.local` in this directory.
3. Fill in `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   from Project Settings -> API in the Supabase dashboard.
4. For the signup flow implemented here (signup immediately logs the
   user in and redirects to `/dashboard`), go to Authentication ->
   Providers -> Email and turn **off** "Confirm email". Email
   verification is intentionally out of scope for this MVP; leaving
   confirmation on means a freshly signed-up user has no session yet,
   and will be bounced back to `/login` from the protected dashboard
   route.
5. Also make sure `apps/api`'s `SUPABASE_JWT_SECRET` (see
   `apps/api/.env.example`) is set from the *same* Supabase project, so
   the backend can verify tokens this frontend issues.

What's implemented and unit-tested (with mocked Supabase clients, no
live project): form validation/error rendering on `/login` and
`/signup`, the login/signup/logout server actions' success and failure
paths, and the route-protection redirect rules in `lib/route-guard.ts`.
What can only be verified against a real Supabase project: the actual
OAuth/password round-trip, session cookie persistence across reloads,
and token refresh in `proxy.ts`/`lib/supabase/middleware.ts`.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
