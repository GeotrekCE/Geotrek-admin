import { ParaglideMessage } from "@inlang/paraglide-js-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { m } from "@/paraglide/messages"

export default function InvalidConfiguration() {
  return (
    <div className="grid h-screen place-items-center">
      <Card className="w-full sm:max-w-md">
        <CardHeader>
          <CardTitle>{m["common.required-config"]()}</CardTitle>
          <CardDescription>
            {m["common.required-config-description"]()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>
            <ParaglideMessage
              message={m["common.required-config-host"]}
              markup={{
                strong: ({ children }) => <Badge>{children}</Badge>,
              }}
            />
            <Button
              variant="link"
              className="p-0"
              render={
                <a
                  target="_blank"
                  href="https://github.com/GeotrekCE/geotrek-admin-mobile"
                >
                  {m["common.documentation"]()}
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
