import * as React from "react"
import { cn } from "@/lib/utils"

const CollapsibleContext = React.createContext<{
  isOpen: boolean
  onOpenChange: (open: boolean) => void
}>({
  isOpen: false,
  onOpenChange: () => {},
})

const Collapsible = React.forwardRef<
  HTMLDivElement,
  {
    open?: boolean
    onOpenChange?: (open: boolean) => void
    children: React.ReactNode
    className?: string
  } & React.HTMLAttributes<HTMLDivElement>
>(({ open, onOpenChange, className, children, ...props }, ref) => {
  const [isOpenState, setIsOpenState] = React.useState(open || false)

  const isControlled = open !== undefined
  const isOpen = isControlled ? open : isOpenState

  const handleOpenChange = (newOpen: boolean) => {
    if (onOpenChange) {
      onOpenChange(newOpen)
    }
    if (!isControlled) {
      setIsOpenState(newOpen)
    }
  }

  return (
    <CollapsibleContext.Provider value={{ isOpen, onOpenChange: handleOpenChange }}>
      <div
        ref={ref}
        data-state={isOpen ? "open" : "closed"}
        className={cn(className)}
        {...props}
      >
        {children}
      </div>
    </CollapsibleContext.Provider>
  )
})
Collapsible.displayName = "Collapsible"

const CollapsibleTrigger = React.forwardRef<
  HTMLButtonElement,
  { asChild?: boolean } & React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ children, asChild, onClick, ...props }, ref) => {
  const { isOpen, onOpenChange } = React.useContext(CollapsibleContext)

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    onOpenChange(!isOpen)
    if (onClick) onClick(e)
  }

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: handleClick,
      "data-state": isOpen ? "open" : "closed",
      ...props,
      // @ts-ignore
      ref,
    })
  }

  return (
    <button
      ref={ref}
      onClick={handleClick}
      data-state={isOpen ? "open" : "closed"}
      {...props}
    >
      {children}
    </button>
  )
})
CollapsibleTrigger.displayName = "CollapsibleTrigger"

const CollapsibleContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => {
  const { isOpen } = React.useContext(CollapsibleContext)

  if (!isOpen) return null

  return (
    <div
      ref={ref}
      className={cn("overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down", className)}
      {...props}
    >
      {children}
    </div>
  )
})
CollapsibleContent.displayName = "CollapsibleContent"

export { Collapsible, CollapsibleTrigger, CollapsibleContent }
