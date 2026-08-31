import * as React from "react"
import { Editor } from "@tiptap/core"
import { Link as LinkIcon } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Link({ editor }: { editor: Editor }) {
  const setLink = React.useCallback(() => {
    const previousUrl = editor.getAttributes("link").href
    const url = window.prompt("URL", previousUrl)

    // cancelled
    if (url === null) {
      return
    }

    // empty
    if (url === "") {
      editor.chain().focus().extendMarkRange("link").unsetLink().run()

      return
    }

    // update link
    try {
      editor
        .chain()
        .focus()
        .extendMarkRange("link")
        .setLink({ href: url })
        .run()
    } catch (e) {
      console.log(e)
    }
  }, [editor])

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Toggle
            size="sm"
            pressed={editor.isActive("link")}
            onPressedChange={setLink}
            disabled={!editor.can().chain().focus().toggleLink().run()}
          >
            <LinkIcon className="size-4" aria-hidden />
            <span className="sr-only">Lien</span>
          </Toggle>
        }
      />
      <TooltipContent>Gras</TooltipContent>
    </Tooltip>
  )
}
