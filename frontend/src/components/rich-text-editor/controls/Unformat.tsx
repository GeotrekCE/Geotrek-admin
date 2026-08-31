import { Editor } from "@tiptap/core"
import { RemoveFormatting } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export default function Unformat({ editor }: { editor: Editor }) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="ghost"
            type="button"
            size="sm"
            onClick={() => editor.chain().focus().unsetAllMarks().run()}
            disabled={!editor.can().chain().focus().unsetAllMarks().run()}
          >
            <RemoveFormatting className="size-4" aria-hidden />
            <span className="sr-only">Supprimer la mise en forme</span>
          </Button>
        }
      />
      <TooltipContent>Supprimer la mise en forme</TooltipContent>
    </Tooltip>
  )
}
