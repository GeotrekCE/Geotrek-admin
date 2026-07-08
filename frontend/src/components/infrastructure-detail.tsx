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
import type { InfrastructureDataSchemaProps } from "@/schemas/data"

export default function InfrastructureDetail(params: {
  id: string
  type: string
}) {
  const navigate = useNavigate()

  const [detail, loaded] = useLiveQuery(
    () =>
      db.infrastructureData
        .get({ id: Number(params.id) })
        .then((data) => [data, true]),
    [],
    []
  )

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "infrastructure",
        id: params.id ? Number(params.id) : undefined,
      })
      .first()
  )

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.infrastructureData.delete(Number(params.id))
    toast.success(`"${detail?.name}" supprimé avec succès`, {
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
        title="Details aménagement"
        withBackbutton
        afterTitle={
          <Link
            className={buttonVariants({ variant: "link" })}
            to="/{-$locale}/data/$type/$id/edit"
            params={params}
          >
            Modifier
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
                <CircleAlert className="size-4" aria-hidden /> Non synchronisé
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">Aménagement</span>
            {detail.type && ` - ${detail.type.name}`}
          </p>
          {detail.conditions.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-1">
              {detail.conditions.map((c) => (
                <Badge key={c.id} variant="outline">
                  {c.name}
                </Badge>
              ))}
            </p>
          )}
          <div className="mt-4">
            <p>Créé le {createDate}</p>
            {createDate !== updateDate && (
              <p>Dernière modification le {updateDate}</p>
            )}
          </div>
        </section>

        {can_bypass_structure && is_superuser && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              Structure liée
            </h3>
            {detail.structure ? (
              <p>{detail.structure.name}</p>
            ) : (
              <p className="italic">Aucune structure liée.</p>
            )}
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Description
          </h3>
          {detail.description ? (
            <div dangerouslySetInnerHTML={{ __html: detail.description }} />
          ) : (
            <p className="italic">Aucune description disponible.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Localisation
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
            Année d'implantation
          </h3>
          {detail.implantation_year ? (
            <p>{detail.implantation_year}</p>
          ) : (
            <p className="italic">Aucune date indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Accessibilité
          </h3>
          {detail.accessibility ? (
            <div dangerouslySetInnerHTML={{ __html: detail.accessibility }} />
          ) : (
            <p className="italic">Aucune accessibilité indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Niveau des usagers
          </h3>
          {detail.usage_difficulty ? (
            <p>{detail.usage_difficulty.name}</p>
          ) : (
            <p className="italic">Aucun niveau indiqué.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Niveau des interventions
          </h3>
          {detail.maintenance_difficulty ? (
            <p>{detail.maintenance_difficulty.name}</p>
          ) : (
            <p className="italic">Aucun niveau indiqué.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Moyen d'accès
          </h3>
          {detail.access ? (
            <p>{detail.access.name}</p>
          ) : (
            <p className="italic">Aucun moyen d'accès indiqué.</p>
          )}
        </section>

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              Modifier l'aménagement
            </Link>
            {detail.appNewItem === true && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                Supprimer l'aménagement
              </Button>
            )}
            {rawDataItem && (
              <Button
                type="button"
                variant="destructive"
                onClick={async () => {
                  await db.rawData
                    .where({ reference: "infrastructure", id: rawDataItem.id })
                    .delete()
                  const { reference: _reference, ...restoredData } = rawDataItem
                  await db.infrastructureData.put(
                    restoredData as InfrastructureDataSchemaProps
                  )
                  toast.success("Restoration de l'aménagement terminée", {
                    position: "top-center",
                  })
                }}
              >
                Annuler les modifications en attente
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
