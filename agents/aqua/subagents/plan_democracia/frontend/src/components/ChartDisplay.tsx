import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export interface ChartDataPoint {
  label: string;
  value: number;
  [key: string]: string | number;
}

export interface ChartData {
  id: string;
  title: string;
  description?: string;
  type: "bar" | "line" | "pie";
  data: ChartDataPoint[];
  dataKey?: string;
  colors?: string[];
}

interface ChartDisplayProps {
  chart: ChartData;
}

const DEFAULT_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

export function ChartDisplay({ chart }: ChartDisplayProps) {
  const colors = chart.colors || DEFAULT_COLORS;
  const dataKey = chart.dataKey || "value";

  const chartConfig: ChartConfig = chart.data.reduce((acc, item, index) => {
    acc[item.label] = {
      label: item.label,
      color: colors[index % colors.length],
    };
    return acc;
  }, {} as ChartConfig);

  chartConfig[dataKey] = {
    label: "Valor",
    color: colors[0],
  };

  // Calcular altura dinámica para bar chart basado en cantidad de datos
  const barChartHeight = Math.max(180, chart.data.length * 40);

  const renderBarChart = () => (
    <BarChart
      data={chart.data}
      layout="vertical"
      margin={{ left: 0, right: 8, top: 8, bottom: 8 }}
    >
      <CartesianGrid horizontal={false} strokeDasharray="3 3" />
      <YAxis
        dataKey="label"
        type="category"
        tickLine={false}
        axisLine={false}
        width={90}
        tick={{ fontSize: 10 }}
        tickFormatter={(value) =>
          value.length > 12 ? `${value.slice(0, 12)}...` : value
        }
      />
      <XAxis type="number" hide />
      <ChartTooltip
        content={<ChartTooltipContent />}
        cursor={{ fill: "hsl(var(--muted))", opacity: 0.3 }}
      />
      <Bar dataKey={dataKey} radius={[0, 4, 4, 0]} barSize={24}>
        {chart.data.map((_, index) => (
          <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
        ))}
      </Bar>
    </BarChart>
  );

  const renderLineChart = () => (
    <LineChart data={chart.data} margin={{ left: 0, right: 8, top: 8, bottom: 8 }}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis
        dataKey="label"
        tickLine={false}
        axisLine={false}
        tick={{ fontSize: 10 }}
        tickFormatter={(value) =>
          value.length > 8 ? `${value.slice(0, 8)}...` : value
        }
      />
      <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 10 }} width={40} />
      <ChartTooltip content={<ChartTooltipContent />} />
      <Line
        type="monotone"
        dataKey={dataKey}
        stroke={colors[0]}
        strokeWidth={2}
        dot={{ fill: colors[0], r: 4 }}
        activeDot={{ r: 6 }}
      />
    </LineChart>
  );

  const renderPieChart = () => (
    <PieChart>
      <ChartTooltip content={<ChartTooltipContent hideLabel />} />
      <Pie
        data={chart.data}
        dataKey={dataKey}
        nameKey="label"
        cx="50%"
        cy="50%"
        innerRadius={35}
        outerRadius={60}
        paddingAngle={2}
      >
        {chart.data.map((_, index) => (
          <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
        ))}
      </Pie>
      <ChartLegend
        content={<ChartLegendContent nameKey="label" />}
        wrapperStyle={{ fontSize: 10 }}
      />
    </PieChart>
  );

  const getChart = () => {
    switch (chart.type) {
      case "bar":
        return renderBarChart();
      case "line":
        return renderLineChart();
      case "pie":
        return renderPieChart();
      default:
        return renderBarChart();
    }
  };

  const getChartHeight = () => {
    switch (chart.type) {
      case "bar":
        return barChartHeight;
      case "pie":
        return 220;
      default:
        return 180;
    }
  };

  return (
    <Card className="w-full max-w-full overflow-hidden">
      <CardHeader className="p-3 pb-1">
        <CardTitle className="text-sm font-medium leading-tight break-words">
          {chart.title}
        </CardTitle>
        {chart.description && (
          <CardDescription className="text-xs leading-tight mt-0.5 break-words">
            {chart.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="p-3 pt-1 overflow-hidden">
        <ChartContainer
          config={chartConfig}
          className="w-full max-w-full [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground"
          style={{ height: getChartHeight() }}
        >
          {getChart()}
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
