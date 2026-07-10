import { m } from "@/paraglide/messages"

export default function Required() {
  return (
    <>
      <span className="text-red-800" aria-hidden>
        *
      </span>
      <span className="text-muted-foreground">({m["form.required"]()})</span>
    </>
  )
}
