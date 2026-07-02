import { Link, useNavigate } from "@tanstack/react-router"
import { useLiveQuery } from "dexie-react-hooks"
import { useList } from "@/lib/list"
import { buttonVariants } from "@/components/ui/button"
import { useStoredDataElement } from "@/hook/useStoredData"
import { getLocale } from "@/paraglide/runtime"
import { db } from "@/lib/db"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"

function ListDetailContent({
  element,
}: {
  element: { id: number; reference: string }
}) {
  const detail = useStoredDataElement(element.reference, element.id)
  const reference = useLiveQuery(
    () => db.references.get(element.reference),
    [element.reference]
  )

  if (!detail) {
    return (
      <SheetContent side="bottom" className="pb-22">
        <SheetHeader>
          <SheetTitle>Élément non trouvé</SheetTitle>
          <SheetDescription>
            L'élément demandé n'existe pas ou plus.
          </SheetDescription>
        </SheetHeader>
      </SheetContent>
    )
  }

  const name = "name" in detail ? detail.name : `Signalement (id: ${detail.id})`

  return (
    <SheetContent side="bottom" className="pb-22">
      <SheetHeader className="pb-0">
        <SheetTitle className="flex items-center gap-2" render={<div />}>
          {reference && "pictogram" in reference && reference.pictogram.url && (
            <img loading="lazy" src={reference.pictogram.url} alt="" />
          )}
          <div>
            <h2 className="text-xl text-accent-foreground">{name}</h2>
            <p>
              <span className="text-primary">{element.reference}</span>
              {"type" in detail && detail.type && ` - ${detail.type.name}`}
            </p>
            {"conditions" in detail && detail.conditions.length > 0 && (
              <p className="mt-1 flex flex-wrap gap-1">
                {detail.conditions.map((c) => (
                  <Badge key={c.id} variant="outline">
                    {c.name}
                  </Badge>
                ))}
              </p>
            )}
            <div className="mt-2 text-xs">
              <p>
                Modifié le{" "}
                {new Date(detail.date_update).toLocaleDateString(getLocale())}
              </p>
            </div>
          </div>
        </SheetTitle>
        {"description" in detail && detail.description && (
          <SheetDescription
            className="mt-4 line-clamp-3"
            dangerouslySetInnerHTML={{ __html: detail.description }}
          />
        )}
      </SheetHeader>
      <SheetFooter>
        <Link
          className={buttonVariants()}
          to="/{-$locale}/data/$type/$id"
          params={{ type: element.reference, id: String(element.id) }}
        >
          Voir le détail
        </Link>
      </SheetFooter>
    </SheetContent>
  )
}

export default function ListDetail() {
  const { filters } = useList()
  const navigate = useNavigate()
  const { focusOn, ...restFilters } = filters

  const handleChange = (open: boolean) => {
    if (!open) {
      navigate({
        to: ".",
        search: restFilters,
      })
    } else {
      navigate({
        to: ".",
        search: filters,
      })
    }
  }

  return (
    <Sheet open={focusOn !== undefined} onOpenChange={handleChange}>
      {focusOn && <ListDetailContent element={focusOn} />}
    </Sheet>
  )
}
