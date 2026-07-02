import { Editor, EditorContent, useEditor } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"
import Undo from "@/components/rich-text-editor/controls/Undo"
import Redo from "@/components/rich-text-editor/controls/Redo"
import Bold from "@/components/rich-text-editor/controls/Bold"
import Italic from "@/components/rich-text-editor/controls/Italic"
import Underline from "@/components/rich-text-editor/controls/Underline"
import Unformat from "@/components/rich-text-editor/controls/Unformat"
import BulletList from "@/components/rich-text-editor/controls/BulletList"
import OrderedList from "@/components/rich-text-editor/controls/OrderedList"
import Link from "@/components/rich-text-editor/controls/Link"

interface MinimalTiptapProps {
  content?: string
  onChange?: (content: string) => void
  placeholder?: string
  editable?: boolean
  className?: string
  isFullPage?: boolean
}

function Controls({ editor }: { editor: Editor }) {
  return (
    <div className="flex flex-wrap items-center gap-1 border-b bg-accent p-2">
      <Undo editor={editor} />
      <Redo editor={editor} />

      <Separator orientation="vertical" className="h-6!" />

      <Bold editor={editor} />
      <Italic editor={editor} />
      <Underline editor={editor} />
      <Link editor={editor} />

      <Separator orientation="vertical" className="h-6!" />

      <BulletList editor={editor} />
      <OrderedList editor={editor} />

      <Separator orientation="vertical" className="h-6!" />

      <Unformat editor={editor} />

      <Separator orientation="vertical" className="h-6!" />
    </div>
  )
}

function RichTextEditor({
  content = "",
  onChange,
  placeholder = "",
  editable = true,
  className,
  isFullPage = false,
}: MinimalTiptapProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
        link: {
          openOnClick: false,
          defaultProtocol: "https",
          protocols: ["http", "https", "mailto", "tel"],
          isAllowedUri: (url, ctx) => {
            try {
              const parsedUrl = url.includes(":")
                ? new URL(url)
                : new URL(`${ctx.defaultProtocol}://${url}`)

              if (!ctx.defaultValidate(parsedUrl.href)) {
                return false
              }

              const protocol = parsedUrl.protocol.replace(":", "")
              const allowedProtocols = ctx.protocols.map((p) =>
                "string" === typeof p ? p : p.scheme
              )

              return allowedProtocols.includes(protocol)
            } catch {
              return false
            }
          },
        },
      }),
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange?.(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: cn(
          "prose prose-sm focus:outline-none",
          "min-h-[200px] border-0 p-4",
          isFullPage && "mx-auto sm:prose-base lg:prose-lg xl:prose-2xl"
        ),
      },
    },
  })

  if (!editor) {
    return null
  }

  return (
    <div className={cn("overflow-hidden rounded-lg border", className)}>
      <Controls editor={editor} />
      <EditorContent
        className="bg-background"
        editor={editor}
        placeholder={placeholder}
      />
    </div>
  )
}

export { RichTextEditor }
