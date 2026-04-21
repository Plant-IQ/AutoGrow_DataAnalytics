/* eslint-disable @next/next/no-img-element */
import { render, screen } from "@testing-library/react";
import useSWR from "swr";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DataSharingApiCard from "@/components/DataSharingApiCard";
import TempHumidityCard from "@/components/GlasshouseCard";
import HealthGauge from "@/components/HealthGauge";
import PumpStatus from "@/components/IrrigationMonitor";
import WeatherCard from "@/components/OutdoorDataCard";

vi.mock("swr", () => ({
  default: vi.fn(),
}));

vi.mock("next/image", () => ({
  default: (props: React.ComponentProps<"img">) => <img alt={props.alt ?? ""} {...props} />,
}));

vi.mock("@/lib/api", () => ({
  fetcher: vi.fn(),
  DEFAULT_LAT: "13.7563",
  DEFAULT_LON: "100.5018",
}));

type SwrResult = {
  data?: unknown;
  isLoading?: boolean;
  error?: unknown;
};

const swrMock = useSWR as unknown as ReturnType<typeof vi.fn>;

function mockSWR(map: Record<string, SwrResult>) {
  swrMock.mockImplementation((key: unknown) => {
    if (key === null) return { isLoading: false, data: undefined, error: undefined };
    if (typeof key !== "string") return { isLoading: false, data: undefined, error: undefined };
    return map[key] ?? { isLoading: false, data: undefined, error: undefined };
  });
}

describe("HealthGauge", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state", () => {
    mockSWR({
      "/plants/active": { isLoading: true },
      "/health": { isLoading: true },
    });

    render(<HealthGauge />);
    expect(screen.getByText("Loading health…")).toBeInTheDocument();
  });

  it("renders no-active-plant state", () => {
    mockSWR({
      "/plants/active": { data: null },
      "/health": { data: { score: 90, components: {} } },
    });

    render(<HealthGauge />);
    expect(screen.getByText("Health score will appear after planting.")).toBeInTheDocument();
  });

  it("renders gauge and component percentages", () => {
    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/health": {
        data: {
          score: 87.5,
          components: { soil: 0.82, temp: 0.91, humidity: 0.79, light: 0.88 },
        },
      },
    });

    render(<HealthGauge />);

    expect(screen.getByText("Health score")).toBeInTheDocument();
    expect(screen.getByText("87.5")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
  });
});

describe("TempHumidityCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading and no-active states", () => {
    mockSWR({
      "/plants/active": { isLoading: true },
      "/history": { isLoading: true },
    });
    const { rerender } = render(<TempHumidityCard />);
    expect(screen.getByText("Loading climate sensors…")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: null },
      "/history": { data: { points: [] } },
    });
    rerender(<TempHumidityCard />);
    expect(screen.getByText("Temperature and humidity appear after a plant starts.")).toBeInTheDocument();
  });

  it("renders latest climate values", () => {
    mockSWR({
      "/plants/active": { data: { id: 2 } },
      "/history": {
        data: {
          points: [
            { ts: "2026-04-21T00:00:00Z", temp: 25.3, humidity: 66 },
            { ts: "2026-04-21T01:00:00Z", temp: 26.1, humidity: 64.2 },
          ],
        },
      },
    });

    render(<TempHumidityCard />);

    expect(screen.getByText("26.1°C")).toBeInTheDocument();
    expect(screen.getByText("64% RH")).toBeInTheDocument();
  });
});

describe("WeatherCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading and error states", () => {
    mockSWR({
      "/context/weather?lat=13.7563&lon=100.5018": { isLoading: true },
    });
    const { rerender } = render(<WeatherCard />);
    expect(screen.getByText("Loading weather…")).toBeInTheDocument();

    mockSWR({
      "/context/weather?lat=13.7563&lon=100.5018": { error: new Error("fail") },
    });
    rerender(<WeatherCard />);
    expect(screen.getByText("Weather unavailable")).toBeInTheDocument();
  });

  it("renders weather values", () => {
    mockSWR({
      "/context/weather?lat=13.7563&lon=100.5018": {
        data: {
          temp_c: 30.45,
          humidity: 76.2,
          sunrise_utc: "2026-04-21T00:00:00Z",
          sunset_utc: "2026-04-21T11:30:00Z",
          source: "open-meteo",
        },
      },
    });

    render(<WeatherCard />);

    expect(screen.getByText("30.4°C")).toBeInTheDocument();
    expect(screen.getByText("76% RH")).toBeInTheDocument();
    expect(screen.getByText("via open-meteo")).toBeInTheDocument();
  });
});

describe("PumpStatus", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading, no-active, and error states", () => {
    mockSWR({
      "/plants/active": { isLoading: true },
      "/pump-status": { isLoading: true },
      "/history": { isLoading: true },
    });
    const { rerender } = render(<PumpStatus />);
    expect(screen.getByText("Loading irrigation telemetry…")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: null },
      "/pump-status": { data: { ok: false, vibration: 0, last_checked: "2026-04-21T00:00:00Z" } },
      "/history": { data: { points: [] } },
    });
    rerender(<PumpStatus />);
    expect(screen.getByText("Irrigation and root-zone data appears after a plant starts.")).toBeInTheDocument();

    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/pump-status": { error: new Error("fail") },
      "/history": { data: { points: [] } },
    });
    rerender(<PumpStatus />);
    expect(screen.getByText("Irrigation telemetry unavailable")).toBeInTheDocument();
  });

  it("renders vibration and soil moisture", () => {
    mockSWR({
      "/plants/active": { data: { id: 1 } },
      "/pump-status": {
        data: { ok: true, vibration: 0.236, last_checked: "2026-04-21T02:30:00Z" },
      },
      "/history": { data: { points: [{ ts: "2026-04-21T02:30:00Z", soil: 48.52 }] } },
    });

    render(<PumpStatus />);

    expect(screen.getByText("Pump active")).toBeInTheDocument();
    expect(screen.getByText("0.24")).toBeInTheDocument();
    expect(screen.getByText("48.5%")).toBeInTheDocument();
  });
});

describe("DataSharingApiCard", () => {
  it("renders endpoint table rows", () => {
    render(<DataSharingApiCard />);

    expect(screen.getByText("Data Sharing API")).toBeInTheDocument();
    expect(screen.getByText("/plants/active")).toBeInTheDocument();
    expect(screen.getByText("/stage/reset")).toBeInTheDocument();
    expect(screen.getByText("No authentication required")).toBeInTheDocument();
  });
});
