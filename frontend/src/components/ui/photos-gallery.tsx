import { m } from "@/paraglide/messages"
import type { AttachmentsSchemaProps } from "@/schemas/attachments"

export default function PhotosGallery({ attachments }: AttachmentsSchemaProps) {
  return (
    <section className="my-8">
      <h3 className="mb-2 text-xl font-bold text-accent-foreground">
        {m["content.attachments-photo-title"]()}
      </h3>

      {attachments && attachments.length > 0 ? (
        <ul className="flex flex-wrap gap-4">
          {attachments
            .filter((attachment) => attachment.value instanceof File)
            .map((attachment, index) => (
              <li key={index} className="flex flex-col items-start gap-2">
                <img
                  src={URL.createObjectURL(attachment.value as File)}
                  alt={`${m["content.attachments-photo-item"]()} ${index + 1}`}
                  className="size-30 rounded-lg bg-primary/15 object-contain"
                />
              </li>
            ))}
        </ul>
      ) : (
        <p className="italic">{m["content.attachments-no-photos"]()}</p>
      )}
    </section>
  )
}
