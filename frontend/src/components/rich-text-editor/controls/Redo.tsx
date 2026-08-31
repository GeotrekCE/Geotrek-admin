import { Editor } from "@tiptap/core"
import { Redo as RedoIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Redo({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().chain().focus().redo().run()}
          >
            <RedoIcon className="size-4" aria-hidden />
            <span className="sr-only">Rétablir</span>
          </Button>
        }
      />
      <TooltipContent>Rétablir</TooltipContent>
    </Tooltip>
  )
}
