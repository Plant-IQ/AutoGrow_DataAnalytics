/* eslint-disable @next/next/no-img-element */
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import useSWR, { mutate } from "swr";
import { beforeEach, describe, expect, it, vi } from "vitest";

import GrowActions from "@/components/GrowActions";
import GrowthStatus from "@/components/GrowthStatus";
import { postJson } from "@/lib/api";

vi.mock("swr", () => ({
  default: vi.fn(),
  mutate: vi.fn(),
}));

vi.mock("next/image", () => ({
  default: ({ priority: _priority, ...props }: React.ComponentProps<"img"> & { priority?: boolean }) => (
    <img alt={props.alt ?? ""} {...props} />
  ),
}));

vi.mock("@/lib/api", () => ({
  fetcher: vi.fn(),
  postJson: vi.fn(),
  DEFAULT_LAT: "13.7563",
  DEFAULT_LON: "100.5018",
}));

type SwrResult = {
  data?: unknown;
  isLoading?: boolean;
  error?: unknown;
};

const swrMock = useSWR as unknown as ReturnType<typeof vi.fn>;
const mutateMock = mutate as unknown as ReturnType<typeof vi.fn>;
const postJsonMock = postJson as unknown as ReturnType<typeof vi.fn>;

function renderGrowthStatusWithSWR(map: Record<string, SwrResult>) {
  swrMock.mockImplementation((key: unknown) => {
    if (key === null) return { isLoading: false, data: undefined, error: undefined };
    if (typeof key !== "string") return { isLoading: false, data: undefined, error: undefined };
    return map[key] ?? { isLoading: false, data: undefined, error: undefined };
  });
  return render(<GrowthStatus />);
}

function renderGrowActionsWithSWR(map: Record<string, SwrResult>) {
  swrMock.mockImplementation((key: unknown) => {
    if (key === null) return { isLoading: false, data: undefined, error: undefined };
    if (typeof key !== "string") return { isLoading: false, data: undefined, error: undefined };
    return map[key] ?? { isLoading: false, data: undefined, error: undefined };
  });
  return render(<GrowActions />);
}

describe("GrowthStatus", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state", () => {
    renderGrowthStatusWithSWR({
      "/plants/active": { isLoading: true },
    });

    expect(screen.getByText("Loading growth status…")).toBeInTheDocument();
  });

  it("renders error state", () => {
    renderGrowthStatusWithSWR({
      "/plants/active": { error: new Error("boom") },
    });

    expect(screen.getByText("Growth status unavailable")).toBeInTheDocument();
  });

  it("renders start form for no active plant and filters suggestions", () => {
    renderGrowthStatusWithSWR({
      "/plants/active": { data: null },
      "/plant-types": {
        data: [
          { id: 1, name: "Lettuce", stage_durations_days: [7, 14, 7] },
          { id: 2, name: "Water Spinach", stage_durations_days: [7, 21, 0] },
        ],
      },
      "/context/weather?lat=13.7563&lon=100.5018": { data: { temp_c: 31 } },
    });

    expect(screen.getByText("Start a new grow")).toBeInTheDocument();
    const input = screen.getByPlaceholderText("e.g., Water Spinach (Morning Glory)");
    fireEvent.change(input, { target: { value: "spin" } });

    expect(screen.getByText("Water Spinach")).toBeInTheDocument();
  });

  it("renders active stage summary and harvest action", async () => {
    postJsonMock.mockResolvedValue({ ok: true, json: async () => ({}) });

    renderGrowthStatusWithSWR({
      "/plants/active": { data: { id: 10, session_code: "00010", label: "Basil", plant_type_id: 1 } },
      "/stage": { data: { stage: 1, label: "Veg", days_in_stage: 5 } },
      "/harvest-eta": { data: { days_to_harvest: 12, projected_date: "2026-05-03T00:00:00Z" } },
      "/plant-types": { data: [{ id: 1, name: "Basil", stage_durations_days: [7, 21, 0] }] },
      "/context/weather?lat=13.7563&lon=100.5018": { data: { temp_c: 30 } },
    });

    expect(screen.getByText("Growth status")).toBeInTheDocument();
    expect(screen.getByAltText("Veg")).toBeInTheDocument();
    expect(screen.getByText(/12 days to harvest/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Harvest" }));

    await waitFor(() => {
      expect(postJsonMock).toHaveBeenCalledWith("/plants/harvest-active", {});
    });
    expect(mutateMock).toHaveBeenCalledWith("/plants/active");
  });
});

describe("GrowActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders active plant summary when available", () => {
    renderGrowActionsWithSWR({
      "/plants/": {
        data: [
          {
            id: 3,
            label: "Lettuce",
            plant_type_id: 2,
            current_stage_index: 0,
            stage_started_at: "2026-01-01T00:00:00Z",
            pending_confirm: false,
          },
        ],
      },
    });

    expect(screen.getByText(/Active plant: Lettuce/)).toBeInTheDocument();
  });

  it("starts a grow plan through plant type + plant + stage reset", async () => {
    postJsonMock
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 9 }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 99 }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    renderGrowActionsWithSWR({
      "/plants/": { data: [] },
    });

    fireEvent.change(screen.getByPlaceholderText("e.g., Basil"), { target: { value: "Basil" } });
    fireEvent.click(screen.getByRole("button", { name: "Save & start" }));

    await waitFor(() => {
      expect(postJsonMock).toHaveBeenCalledWith("/plant-types", {
        name: "Basil",
        stage_durations_days: [7, 21, 28],
        stage_colors: ["#4DA6FF", "#FFFFFF", "#FF6FA3"],
      });
    });

    expect(postJsonMock).toHaveBeenCalledWith("/plants/", {
      label: "Basil",
      plant_type_id: 9,
    });
    expect(postJsonMock).toHaveBeenCalledWith("/stage/reset", {});
    expect(mutateMock).toHaveBeenCalledWith("/plants/");
    expect(screen.getAllByText("Grow plan started")).toHaveLength(2);
  });

  it("resets cycle", async () => {
    postJsonMock.mockResolvedValue({ ok: true, json: async () => ({}) });

    renderGrowActionsWithSWR({
      "/plants/": { data: [] },
    });

    fireEvent.click(screen.getByRole("button", { name: "Reset cycle to Seed" }));

    await waitFor(() => {
      expect(postJsonMock).toHaveBeenCalledWith("/stage/reset", {});
    });
    expect(screen.getAllByText("Cycle reset to seed")).toHaveLength(2);
  });
});
