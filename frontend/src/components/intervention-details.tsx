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
import { dateCompare } from "@/lib/date"
import NotFound from "@/components/not-found"
import { usePermission } from "@/hook/useSettingsQuery"

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
  const syncData = useLiveQuery(() => db.appSync.get("data"))

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.interventionData.delete(Number(id))
    toast.success(`"${detail?.name}" supprimé avec succès`, {
      position: "top-center",
    })
    navigate({
      to: "/{-$locale}",
    })
  }, [detail?.name, navigate])

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

  const isAsyncItem = dateCompare(detail.date_update, syncData?.lastSync) > -1

  return (
    <div>
      <Header
        title="Details intervention"
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
            <span className="text-primary">Intervention</span>
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
          {detail.api_geom && (
            <Map
              className="pointer-none aspect-square touch-none"
              longitude={detail.api_geom.coordinates[0]}
              latitude={detail.api_geom.coordinates[1]}
            >
              <Marker
                longitude={detail.api_geom.coordinates[0]}
                latitude={detail.api_geom.coordinates[1]}
                anchor="bottom"
              />
            </Map>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Date de début
          </h3>
          <p>{detail.begin_date}</p>
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Date de fin
          </h3>
          {detail.end_date ? (
            <p>{detail.end_date}</p>
          ) : (
            <p className="italic">Aucune date de fin indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Statut
          </h3>
          <p>{detail.status.name}</p>
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Longueur
          </h3>
          {detail.length ? (
            <p>{detail.length}</p>
          ) : (
            <p className="italic">Aucune longueur indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Largeur
          </h3>
          {detail.width ? (
            <p>{detail.width}</p>
          ) : (
            <p className="italic">Aucune largeur indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Hauteur
          </h3>
          {detail.height ? (
            <p>{detail.height}</p>
          ) : (
            <p className="italic">Aucune hauteur indiquée.</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Enjeu
          </h3>
          {detail.stake ? (
            <p>{detail.stake.name}</p>
          ) : (
            <p className="italic">Aucun enjeu indiqué.</p>
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

        <section className="my-8">
          <h3 className="mb-2 flex items-center gap-2 text-xl font-bold text-accent-foreground">
            Jours hommes{" "}
            <Badge className="size-6">{detail.man_day.length}</Badge>
          </h3>
          {detail.man_day.length > 0 ? (
            <ul>
              {detail.man_day.map((row, index) => (
                <li key={index} className="my-2 rounded-lg border px-4 py-2">
                  <div className="my-2 flex gap-3">
                    <h4 className="font-semibold">Nombre de jour :</h4>
                    <p>{row.nb_days}</p>
                  </div>

                  <div className="my-2 flex gap-3">
                    <h4 className="font-semibold">Fonction :</h4>
                    <p>{row.job.name}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="italic">Aucune affectation.</p>
          )}
        </section>

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              Modifier {params.type}
            </Link>
            {dateCompare(detail.date_insert, syncData?.lastSync) > -1 && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                Supprimer {params.type}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
