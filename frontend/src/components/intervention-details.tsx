import * as React from "react"
import Header from "@/components/header"
import { getLocale } from "@/paraglide/runtime"
import { Link, useNavigate } from "@tanstack/react-router"
import Map from "@/components/map"
import { Marker } from "react-map-gl/maplibre"
import { Badge } from "@/components/ui/badge"
import { CircleAlert } from "lucide-react"
import { Button, buttonVariants } from "@/components/ui/button"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import NotFound from "@/components/not-found"
import { usePermission } from "@/hook/useSettingsQuery"
import type { InterventionDataSchemaProps } from "@/schemas/data"
import { m } from "@/paraglide/messages"

export default function InterventionDetail(params: {
  id: string
  type: string
}) {
  const navigate = useNavigate()

  const [detail, loaded] = useLiveQuery(
    () =>
      db.interventionData
        .get({ id: Number(params.id) })
        .then((data) => [data, true]),
    [],
    []
  )
  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "intervention",
        id: params.id ? Number(params.id) : undefined,
      })
      .first()
  )

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.interventionData.delete(Number(params.id))
    toast.success(m["common.delete-success"]({ item: detail?.name ?? "" }), {
      position: "top-center",
    })
    navigate({
      to: "/{-$locale}",
    })
  }, [detail?.name, navigate, params.id])

  const { can_bypass_structure, is_superuser } = usePermission()

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
        title={m["content.details.intervention"]()}
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
              {detail.name}
            </span>
            {isAsyncItem && (
              <span className="flex items-center gap-2 text-sm text-destructive">
                <CircleAlert className="size-4" aria-hidden />{" "}
                {m["content.not-synced"]()}
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">{m["content.intervention"]()}</span>
            {detail.type && ` - ${detail.type.name}`}
          </p>
          {detail.disorders.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-1">
              {detail.disorders.map((c) => (
                <Badge key={c.id} variant="outline">
                  {c.name}
                </Badge>
              ))}
            </p>
          )}

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

        {can_bypass_structure && is_superuser && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              {m["content.linked-structure"]()}
            </h3>
            {detail.structure ? (
              <p>{detail.structure.name}</p>
            ) : (
              <p className="italic">{m["content.no-linked-structure"]()}</p>
            )}
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.description"]()}
          </h3>
          {detail.description ? (
            <div dangerouslySetInnerHTML={{ __html: detail.description }} />
          ) : (
            <p className="italic">{m["content.no-description"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.location"]()}
          </h3>
          {detail.geom && (
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
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.begin-date"]()}
          </h3>
          <p>{detail.begin_date}</p>
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.end-date"]()}
          </h3>
          {detail.end_date ? (
            <p>{detail.end_date}</p>
          ) : (
            <p className="italic">{m["content.no-end-date"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.status"]()}
          </h3>
          <p>{detail.status.name}</p>
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.length"]()}
          </h3>
          {detail.length ? (
            <p>{detail.length}</p>
          ) : (
            <p className="italic">{m["content.no-length"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.width"]()}
          </h3>
          {detail.width ? (
            <p>{detail.width}</p>
          ) : (
            <p className="italic">{m["content.no-width"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.height"]()}
          </h3>
          {detail.height ? (
            <p>{detail.height}</p>
          ) : (
            <p className="italic">{m["content.no-height"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.stake"]()}
          </h3>
          {detail.stake ? (
            <p>{detail.stake.name}</p>
          ) : (
            <p className="italic">{m["content.no-stake"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.access"]()}
          </h3>
          {detail.access ? (
            <p>{detail.access.name}</p>
          ) : (
            <p className="italic">{m["content.no-access"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 flex items-center gap-2 text-xl font-bold text-accent-foreground">
            {m["content.man-days"]()}{" "}
            <Badge className="size-6">{detail.man_day.length}</Badge>
          </h3>
          {detail.man_day.length > 0 ? (
            <ul>
              {detail.man_day.map((row, index) => (
                <li key={index} className="my-2 rounded-lg border px-4 py-2">
                  <div className="my-2 flex gap-3">
                    <h4 className="font-semibold">
                      {m["content.number-of-days"]()}
                    </h4>
                    <p>{row.nb_days}</p>
                  </div>

                  <div className="my-2 flex gap-3">
                    <h4 className="font-semibold">{m["content.function"]()}</h4>
                    <p>{row.job.name}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="italic">{m["content.no-man-days"]()}</p>
          )}
        </section>

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              {m["common.edit-item"]({ item: m["content.intervention"]() })}
            </Link>
            {detail.appNewItem === true && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                {m["common.delete-item"]({ item: m["content.intervention"]() })}
              </Button>
            )}
            {rawDataItem && (
              <Button
                type="button"
                variant="destructive"
                onClick={async () => {
                  await db.rawData
                    .where({ reference: "intervention", id: rawDataItem.id })
                    .delete()
                  const { reference: _reference, ...restoredData } = rawDataItem
                  await db.interventionData.put(
                    restoredData as InterventionDataSchemaProps
                  )
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
