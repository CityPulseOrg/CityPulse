import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { vi } from "vitest"

import AdminPage from "@/app/admin/page"

vi.mock("@/lib/api", () => ({
  getIssues: vi.fn().mockResolvedValue([]),
  getIssue: vi.fn().mockResolvedValue(null),
  updateIssueStatus: vi.fn().mockResolvedValue(undefined),
}))

const renderAdminPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AdminPage />
    </QueryClientProvider>
  )
}

test("category filter values match backend enum order", async () => {
  renderAdminPage()
  const user = userEvent.setup()
  const trigger = screen.getByText("All Categories").closest("button")
  if (!trigger) {
    throw new Error("Category filter trigger not found")
  }
  await user.click(trigger)

  const options = await screen.findAllByRole("option")
  const labels = options.map((option) =>
    (option.textContent || "").replace(/^[^A-Za-z0-9]+\s*/, "").trim()
  )

  expect(labels).toEqual([
    "All Categories",
    "Pothole",
    "Broken Streetlight",
    "Broken Sign",
    "Illegal Dumping",
    "Graffiti",
    "Vandalism",
    "Overgrown Grass",
    "Unplowed Area",
    "Icy Street",
    "Icy Sidewalk",
    "Malfunctioning Water Fountain",
    "Other",
  ])
})
