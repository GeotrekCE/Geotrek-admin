import * as React from "react"
import { m } from "@/paraglide/messages"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function DetailConfirmButton({
  onClick,
  reason,
  ...props
}: React.ComponentProps<typeof Button> & { reason: string }) {
  const [open, setOpen] = React.useState(false)

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger
        render={
          <Button className="h-auto py-2 whitespace-normal" {...props}>
            {reason}
          </Button>
        }
      ></AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            <strong>
              {m["content.confirm-dialog-title"]({
                reason: reason.toLocaleLowerCase(),
              })}
            </strong>
          </AlertDialogTitle>
          <AlertDialogDescription>
            {m["content.confirm-dialog-description"]()}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <Button onClick={() => setOpen(false)} variant="outline">
          {m["common.cancel"]()}
        </Button>
        <Button
          onClick={(event) => {
            event.preventDefault()
            onClick?.(event)
            scrollTo({ top: 0, behavior: "smooth" })
          }}
          type="reset"
        >
          {m["common.confirm"]()}
        </Button>
      </AlertDialogContent>
    </AlertDialog>
  )
}
