import * as React from "react"
import Header from "@/components/header"
import { getLocale } from "@/paraglide/runtime"
import { Link, useNavigate } from "@tanstack/react-router"
import Map from "@/components/map"
import { Marker } from "react-map-gl/maplibre"
import { CircleAlert } from "lucide-react"
import { Button, buttonVariants } from "@/components/ui/button"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import NotFound from "@/components/not-found"
import type { ReportDataSchemaProps } from "@/schemas/data"
import { m } from "@/paraglide/messages"

export default function ReportDetail(params: { id: string; type: string }) {
  const navigate = useNavigate()

  const [detail, loaded] = useLiveQuery(
    () =>
      db.reportData.get({ id: Number(params.id) }).then((data) => [data, true]),
    [],
    []
  )
  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "report",
        id: params.id ? Number(params.id) : undefined,
      })
      .first()
  )

  const name = `Signalement (id: ${params.id})`

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.reportData.delete(Number(params.id))
    toast.success(`"${name}" supprimé avec succès`, { position: "top-center" })
    navigate({
      to: "/{-$locale}",
    })
  }, [name, navigate, params.id])

  if (!loaded) {
    return null
  }

  if (!detail) {
    return <NotFound />
  }
  const createDate = new Date(detail.date_insert).toLocaleDateString(
    getLocale()
  )
  const updateDate = new Date(detail.date_update).toLocaleDateString(
    getLocale()
  )

  const isAsyncItem = detail.appSynced === false

  return (
    <div>
      <Header
        title={m["content.details.report"]()}
        withBackbutton
        afterTitle={
          <Link
            className={buttonVariants({ variant: "link" })}
            to="/{-$locale}/data/$type/$id/edit"
            params={params}
          >
            {m["common.edit"]()}
          </Link>
        }
      />
      <div className="m-auto max-w-140 p-4">
        <section>
          <h2 className="flex flex-wrap justify-between">
            <span className="text-2xl font-medium text-accent-foreground">
              {name}
            </span>
            {isAsyncItem && (
              <span className="flex items-center gap-2 text-sm text-destructive">
                <CircleAlert className="size-4" aria-hidden />{" "}
                {m["content.not-synced"]()}
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">{m["content.report"]()}</span>
          </p>
          <div className="mt-4">
            <p>
              {m["content.created-on"]()} {createDate}
            </p>
            {createDate !== updateDate && (
              <p>
                {m["content.updated-on"]()} {updateDate}
              </p>
            )}
          </div>
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.comment"]()}
          </h3>
          {detail.comment ? (
            <div dangerouslySetInnerHTML={{ __html: detail.comment }} />
          ) : (
            <p className="italic">{m["content.no-comment"]()}</p>
          )}
        </section>

        {detail.geom && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              {m["content.location"]()}
            </h3>
            <Map
              className="pointer-none aspect-square touch-none"
              longitude={detail.geom.coordinates[0]}
              latitude={detail.geom.coordinates[1]}
            >
              <Marker
                longitude={detail.geom.coordinates[0]}
                latitude={detail.geom.coordinates[1]}
                anchor="bottom"
              />
            </Map>
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.activity"]()}
          </h3>
          {detail.activity ? (
            <p>{detail.activity.name}</p>
          ) : (
            <p className="italic">{m["content.no-activity"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.category"]()}
          </h3>
          {detail.category ? (
            <p>{detail.category.name}</p>
          ) : (
            <p className="italic">{m["content.no-category"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.problem-magnitude"]()}
          </h3>
          {detail.problem_magnitude ? (
            <p>{detail.problem_magnitude.name}</p>
          ) : (
            <p className="italic">{m["content.no-problem-magnitude"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.status"]()}
          </h3>
          {detail.status ? (
            <p>{detail.status.name}</p>
          ) : (
            <p className="italic">{m["content.no-status"]()}</p>
          )}
        </section>

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              {m["common.edit-item"]({ item: m["content.report"]() })}
            </Link>
            {detail.appNewItem === true && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                {m["common.delete-item"]({ item: m["content.report"]() })}
              </Button>
            )}
            {rawDataItem && (
              <Button
                type="button"
                variant="destructive"
                onClick={async () => {
                  await db.rawData
                    .where({ reference: "report", id: rawDataItem.id })
                    .delete()
                  const { reference: _reference, ...restoredData } = rawDataItem
                  await db.reportData.put(restoredData as ReportDataSchemaProps)
                  toast.success(m["content.restore-complete"](), {
                    position: "top-center",
                  })
                }}
              >
                {m["content.restore-pending"]()}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
