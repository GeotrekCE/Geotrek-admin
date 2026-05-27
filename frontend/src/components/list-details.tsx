import { Link, useNavigate } from "@tanstack/react-router"
import { useList } from "@/lib/list"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { buttonVariants } from "@/components/ui/button"
import { useStoredDataElement } from "@/hook/useStoredData"
import { getLocale } from "@/paraglide/runtime"
import { Badge } from "./ui/badge"

function ListDetailContent({
  element,
}: {
  element: { id: number; reference: string }
}) {
  const details = useStoredDataElement(element.reference, element.id)
  if (!details) {
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
  console.log(details)
  return (
    <SheetContent side="bottom" className="pb-22">
      <SheetHeader className="pb-0">
        <SheetTitle className="flex items-center gap-2" render={<div />}>
          {details.pictogram.url && (
            <img loading="lazy" src={details.pictogram.url} alt="" />
          )}
          <div>
            <h2 className="text-xl text-accent-foreground">{details.name}</h2>
            <p>
              <span className="text-primary">{details.reference}</span>
              {"type" in details && ` - ${details.type.name}`}
            </p>
            {"conditions" in details && details.conditions.length > 0 && (
              <p className="mt-1 flex flex-wrap gap-1">
                {details.conditions.map((c) => (
                  <Badge key={c.id} variant="outline">
                    {c.name}
                  </Badge>
                ))}
              </p>
            )}
            <div className="mt-2 text-xs">
              <p>
                Modifié le{" "}
                {new Date(details.date_update).toLocaleDateString(getLocale())}
              </p>
            </div>
          </div>
        </SheetTitle>
        {"description" in details && details.description && (
          <SheetDescription
            className="mt-4 line-clamp-3"
            dangerouslySetInnerHTML={{ __html: details.description }}
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
