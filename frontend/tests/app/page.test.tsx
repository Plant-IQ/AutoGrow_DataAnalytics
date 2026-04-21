/* eslint-disable @next/next/no-img-element */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

vi.mock("next/image", () => ({
  default: (props: React.ComponentProps<"img">) => <img alt={props.alt ?? ""} {...props} />,
}));

vi.mock("@/components/IrrigationMonitor", () => ({ default: () => <div>PumpStatus Stub</div> }));
vi.mock("@/components/SensorChart", () => ({ default: () => <div>SensorChart Stub</div> }));
vi.mock("@/components/LightStatus", () => ({ default: () => <div>PlantLight Stub</div> }));
vi.mock("@/components/GlasshouseCard", () => ({ default: () => <div>TempHumidityCard Stub</div> }));
vi.mock("@/components/OutdoorDataCard", () => ({ default: () => <div>WeatherCard Stub</div> }));
vi.mock("@/components/GrowthStatus", () => ({ default: () => <div>GrowthStatus Stub</div> }));
vi.mock("@/components/SoilHumidityScatter", () => ({ default: () => <div>SoilHumidityScatter Stub</div> }));
vi.mock("@/components/TemperatureComparisonScatter", () => ({ default: () => <div>TemperatureComparisonScatter Stub</div> }));
vi.mock("@/components/DailyTempHumidityComparisonBarChart", () => ({
  default: () => <div>DailyTempHumidityComparisonBarChart Stub</div>,
}));
vi.mock("@/components/SoilMoisturePumpChart", () => ({ default: () => <div>SoilMoisturePumpChart Stub</div> }));
vi.mock("@/components/DataSharingApiCard", () => ({ default: () => <div>DataSharingApiCard Stub</div> }));

describe("Home page", () => {
  it("renders dashboard frame and child sections", () => {
    render(<Home />);

    expect(screen.getByText("Grow room overview")).toBeInTheDocument();
    expect(screen.getByText("GrowthStatus Stub")).toBeInTheDocument();
    expect(screen.getByText("PlantLight Stub")).toBeInTheDocument();
    expect(screen.getByText("DataSharingApiCard Stub")).toBeInTheDocument();
  });
});
