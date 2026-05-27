import * as React from "react"
import { Drawer } from "@base-ui/react"
import { ChevronRight } from "lucide-react"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "./ui/item"
import { Link } from "@tanstack/react-router"
import { cn } from "@/lib/utils"
import { useList, type SnapPoint } from "@/lib/list"
import { getLocale } from "@/paraglide/runtime"

const TOP_MARGIN_REM = 1

export default function List() {
  const { elements, filters, snapPoint, setSnapPoint, snapPoints } = useList()

  return (
    <Drawer.Root
      open={filters.focusOn === undefined}
      snapPoints={snapPoints}
      modal={false}
      disablePointerDismissal
      snapToSequentialPoints
      onSnapPointChange={(value) => setSnapPoint(value as SnapPoint)}
      snapPoint={snapPoint}
    >
      <Drawer.Portal keepMounted>
        <Drawer.Viewport className="pointer-events-none fixed inset-0 top-16 z-10 flex touch-none items-end justify-center">
          <Drawer.Popup
            className={cn(
              "pointer-events-auto relative flex h-[calc(100dvh-var(--top-margin))] w-full translate-y-(--drawHeight) touch-none flex-col overflow-visible rounded-t-2xl bg-background pb-[max(0px,var(--drawHeight)+5.4rem)] shadow-2xl transition-transform will-change-transform data-ending-style:translate-y-[calc(100%+2px)] data-ending-style:pb-0 data-ending-style:duration-[calc(var(--drawer-swipe-strength)*0.4s)] data-starting-style:translate-y-[calc(100%+2px)] data-starting-style:pb-0 data-swiping:select-none",
              snapPoint === 1 && "border-top rounded-none"
            )}
            style={
              {
                "--top-margin": `${TOP_MARGIN_REM}rem`,
                "--drawHeight": `calc(var(--drawer-snap-point-offset) + var(--drawer-swipe-movement-y))`,
              } as React.CSSProperties
            }
          >
            <div className="shrink-0 touch-none border-b px-6 py-3.5">
              <div className="mx-auto mb-2 h-2 w-20 shrink-0 rounded-full bg-accent" />
              <Drawer.Title className="text-l text-center font-bold">
                {elements.length} éléments
              </Drawer.Title>
            </div>
            <Drawer.Content className="min-h-0 flex-1 touch-auto overflow-y-auto overscroll-contain pt-2">
              <div className="m-auto h-full w-full max-w-120 px-4">
                <ul
                  className={cn(
                    "transition-opacity",
                    snapPoint === snapPoints[0] ? "opacity-0" : "opacity-100"
                  )}
                >
                  {elements.length === 0 && (
                    <p className="py-4 text-center">
                      Aucun élément à afficher.
                    </p>
                  )}
                  {elements.map((item) => (
                    <li key={`${item.reference}-${item.id}`} className="my-4">
                      <Item
                        variant="outline"
                        className="bg-accent"
                        render={
                          <Link
                            to={`/data/$type/$id`}
                            params={{
                              id: item.id.toString(),
                              type: item.reference,
                            }}
                          >
                            <ItemMedia>
                              <img src={item.pictogram.url} alt="" />
                            </ItemMedia>
                            <ItemContent>
                              <ItemTitle className="text-accent-foreground">
                                {item.name}
                              </ItemTitle>
                              {"description" in item && (
                                <ItemDescription
                                  dangerouslySetInnerHTML={{
                                    __html: item.description,
                                  }}
                                />
                              )}
                              <time
                                dateTime={item.date_update}
                                className="text-xs text-muted-foreground"
                              >
                                Modifié le{" "}
                                {new Date(item.date_update).toLocaleDateString(
                                  getLocale(),
                                  {
                                    year: "numeric",
                                    month: "long",
                                    day: "numeric",
                                  }
                                )}
                              </time>
                            </ItemContent>
                            <ItemActions>
                              <ChevronRight aria-hidden />
                            </ItemActions>
                          </Link>
                        }
                      />
                    </li>
                  ))}
                </ul>
              </div>
            </Drawer.Content>
            <div className="pointer-none absolute inset-x-0 top-full h-12" />
          </Drawer.Popup>
        </Drawer.Viewport>
      </Drawer.Portal>
    </Drawer.Root>
  )
}
