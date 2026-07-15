import { Editor } from "@tiptap/core"
import { Undo as UndoIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Undo({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().chain().focus().undo().run()}
          >
            <UndoIcon className="size-4" aria-hidden />
            <span className="sr-only">Annuler</span>
          </Button>
        }
      />
      <TooltipContent>Annuler</TooltipContent>
    </Tooltip>
  )
}
