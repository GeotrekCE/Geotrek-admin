import * as React from "react"
import { useNavigate } from "@tanstack/react-router"
import { useForm } from "@tanstack/react-form"
import Header from "@/components/header"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetFooter,
  SheetTrigger,
} from "@/components/ui/sheet"
import { ListFilter, Search } from "lucide-react"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import type { ListSearchParams } from "../routes/_authenticated/index"
import { Badge } from "@/components/ui/badge"

export default function ListFilters({
  filters = {},
}: {
  filters: ListSearchParams
}) {
  const navigate = useNavigate()
  const [open, setOpen] = React.useState(false)

  const form = useForm({
    defaultValues: {
      type: filters.type as ListSearchParams["type"],
    },
    onSubmit: async ({ value }) => {
      navigate({
        to: ".",
        search: {
          ...filters,
          type: value.type && value.type.length > 0 ? value.type : undefined,
        },
      })
    },
  })

  const hasTypeFilter = filters.type && filters.type.length > 0

  return (
    <div className="flex gap-2 p-4">
      <InputGroup>
        <InputGroupInput
          defaultValue={filters.q}
          type="search"
          placeholder="Rechercher"
          onChange={(event) => {
            const nextValue = event.target.value
            navigate({
              to: ".",
              search: { ...filters, q: nextValue.toString() || undefined },
              replace: true,
            })
          }}
        />
        <InputGroupAddon>
          <Search
            type="search"
            aria-label="Rechercher"
            className="text-accent-foreground"
          />
        </InputGroupAddon>
      </InputGroup>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger
          render={
            <Button variant="outline">
              <ListFilter aria-hidden />
              Filtres
              {hasTypeFilter && (
                <Badge className="size-5 text-xs">{filters.type?.length}</Badge>
              )}
            </Button>
          }
        />
        <SheetContent showCloseButton={false} className="w-full! max-w-full!">
          <form
            onSubmit={(event) => {
              event.preventDefault()
              form.handleSubmit()
              setOpen(false)
            }}
          >
            <Header
              title="Filtres"
              beforeTitle={
                <SheetClose render={<Button variant="link">Annuler</Button>} />
              }
              afterTitle={
                hasTypeFilter && (
                  <Button
                    variant="link"
                    onClick={() => {
                      navigate({
                        to: ".",
                      })
                      form.reset()
                      form.setFieldValue("type", [])
                      setOpen(false)
                    }}
                  >
                    Effacer tout
                  </Button>
                )
              }
            />
            <div className="p-4">
              <div className="flex items-center justify-between">
                <h2 className="my-3 font-bold">Type(s) d'objets</h2>
                {hasTypeFilter && (
                  <Badge className="size-6">{filters.type?.length}</Badge>
                )}
              </div>
              <form.Field
                name="type"
                children={(field) => (
                  <ToggleGroup
                    className="mb-8 flex-wrap bg-background p-1"
                    size="sm"
                    spacing={2}
                    value={field.state.value}
                    onValueChange={(value) =>
                      field.handleChange(value as ListSearchParams["type"])
                    }
                    multiple
                  >
                    <ToggleGroupItem
                      className="bg-primary/20 text-primary hover:bg-primary hover:text-primary-foreground data-pressed:bg-primary data-pressed:text-primary-foreground"
                      value="signage"
                    >
                      Signalétiques
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      className="bg-primary/20 text-primary hover:bg-primary hover:text-primary-foreground data-pressed:bg-primary data-pressed:text-primary-foreground"
                      value="intervention"
                    >
                      Interventions
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      className="bg-primary/20 text-primary hover:bg-primary hover:text-primary-foreground data-pressed:bg-primary data-pressed:text-primary-foreground"
                      value="report"
                    >
                      Signalement
                    </ToggleGroupItem>
                    <ToggleGroupItem
                      className="bg-primary/20 text-primary hover:bg-primary hover:text-primary-foreground data-pressed:bg-primary data-pressed:text-primary-foreground"
                      value="infrastructure"
                    >
                      Aménagement
                    </ToggleGroupItem>
                  </ToggleGroup>
                )}
              />
            </div>
            <SheetFooter className="pb-27">
              <Button type="submit" className="w-full">
                Appliquer les filtres
              </Button>
            </SheetFooter>
          </form>
        </SheetContent>
      </Sheet>
    </div>
  )
}
