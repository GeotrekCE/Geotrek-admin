import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function InvalidConfiguration() {
  return (
    <div className="grid h-screen place-items-center">
      <Card className="w-full sm:max-w-md">
        <CardHeader>
          <CardTitle>Configuration requise</CardTitle>
          <CardDescription>
            Veuillez configurer l'URL de votre instance Geotrek-Admin dans le
            fichier de configuration pour utiliser l'application.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>
            La clé <Badge variant="outline">HOST_URL</Badge> doit être définie
            en tant que variable d'environnement pour permettre la connexion et
            la synchronisation des données.{" "}
            <Button
              variant="link"
              className="p-0"
              render={
                <a
                  target="_blank"
                  href="https://github.com/GeotrekCE/geotrek-admin-mobile"
                >
                  Voir la documentation
                </a>
              }
            />
            .
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
