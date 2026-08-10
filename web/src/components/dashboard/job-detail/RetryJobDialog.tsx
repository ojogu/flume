import { Loader2 } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

export function RetryJobDialog({
  open,
  retrying,
  retryCount,
  maxRetries,
  onOpenChange,
  onConfirm,
}: {
  open: boolean
  retrying: boolean
  retryCount: number
  maxRetries: number
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="text-display text-2xl">Retry this job?</AlertDialogTitle>
          <AlertDialogDescription>
            This restarts the job from the beginning. {retryCount === 0 ? 'This will be your first retry.' : `The job is on attempt ${retryCount + 1} of ${maxRetries}.`}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={retrying}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={retrying} className="gap-2">
            {retrying && <Loader2 className="h-4 w-4 animate-spin" />}
            {retrying ? 'Retrying…' : 'Retry job'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
