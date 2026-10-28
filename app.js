/**
 * Revenue.OS // Plastic Waste Intelligence Dashboard
 * Pure Client-Side Architecture (Plotly.js + Vanilla JS)
 * Zero backend serverless dependency - 100% Vercel & Browser Compatible
 */

(function () {
  'use strict';

  // 1. GLOBAL BASELINES & PALETTES
  const BASELINE = {
    waste: 1.7235,
    recycling: 13.096,
    perCapita: 122.255,
  };

  const RISK_COLORS = {
    Low: '#10B981',
    Medium: '#06B6D4',
    High: '#F59E0B',
    Very_High: '#EF4444',
  };

  const RISK_ORDER = ['Low', 'Medium', 'High', 'Very_High'];

  // Current State
  let currentTheme = localStorage.getItem('revenue_os_theme') || 'dark';
  let activeTab = 'analytics';
  let scatterLogScale = false;
  let recSortMode = 'highest';
  let recScope = 15;
  let benchmarkCohort = ['China', 'United States', 'Germany', 'India'];
  let dossierCountry = 'United States';
  let ledgerQuery = '';
  let ledgerSortCol = 'Total_Plastic_Waste_MT';
  let ledgerSortAsc = false;

  // Filter Values
  let filterSearch = '';
  let filterNations = new Set();
  let filterRisks = new Set();
  let filterSources = new Set();
  let filterRecMin = 0.1;
  let filterRecMax = 84.8;
  let filterWasteMin = 0.01;
  let filterWasteMax = 59.08;

  const dataset = (window.RAW_DATASET || []).slice();

  // 2. HELPER FUNCTIONS
  function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) return '0.00';
    return Number(num).toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  function getPlotlyTheme() {
    const isDark = currentTheme === 'dark';
    return {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {
        family: "'Plus Jakarta Sans', -apple-system, sans-serif",
        color: isDark ? '#FFFFFF' : '#0F172A',
        size: 11,
      },
      gridcolor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      zerolinecolor: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)',
    };
  }

  // 3. FILTERING LOGIC
  function getFilteredDataset() {
    return dataset.filter(item => {
      // 1. Country search
      if (filterSearch && !item.Country.toLowerCase().includes(filterSearch.toLowerCase())) {
        return false;
      }
      // 2. Nation multi-selection
      if (filterNations.size > 0 && !filterNations.has(item.Country)) {
        return false;
      }
      // 3. Coastal Risk
      if (filterRisks.size > 0 && !filterRisks.has(item.Coastal_Waste_Risk)) {
        return false;
      }
      // 4. Source Sector
      if (filterSources.size > 0 && !filterSources.has(item.Main_Sources)) {
        return false;
      }
      // 5. Recycling range
      if (item.Recycling_Rate < filterRecMin || item.Recycling_Rate > filterRecMax) {
        return false;
      }
      // 6. Total Waste range
      if (item.Total_Plastic_Waste_MT < filterWasteMin || item.Total_Plastic_Waste_MT > filterWasteMax) {
        return false;
      }
      return true;
    });
  }

  // 4. HERO KPI CARDS
  function renderHeroKPIs(filtered) {
    const totalWaste = filtered.reduce((acc, c) => acc + (c.Total_Plastic_Waste_MT || 0), 0);
    const globalTotalWaste = dataset.reduce((acc, c) => acc + (c.Total_Plastic_Waste_MT || 0), 0);
    const wasteShare = globalTotalWaste > 0 ? (totalWaste / globalTotalWaste) * 100 : 0;

    const avgRecycling = filtered.length > 0
      ? filtered.reduce((acc, c) => acc + (c.Recycling_Rate || 0), 0) / filtered.length
      : 0;
    const recDelta = avgRecycling - BASELINE.recycling;

    const totalValuation = filtered.reduce((acc, c) => acc + (c.Material_Valuation_USD_M || 0), 0);

    const highRiskCount = filtered.filter(c => c.Coastal_Waste_Risk === 'High' || c.Coastal_Waste_Risk === 'Very_High').length;
    const riskPct = filtered.length > 0 ? (highRiskCount / filtered.length) * 100 : 0;

    const avgPerCapita = filtered.length > 0
      ? filtered.reduce((acc, c) => acc + (c.Per_Capita_Waste_KG || 0), 0) / filtered.length
      : 0;

    // Waste Card
    document.getElementById('kpi-waste-val').innerHTML = `${formatNumber(totalWaste, 2)} <span class="rev-card-unit">MT</span>`;
    document.getElementById('kpi-waste-trend').textContent = `${formatNumber(wasteShare, 1)}% Global Share`;

    // Recycling Card
    document.getElementById('kpi-rec-val').innerHTML = `${formatNumber(avgRecycling, 2)}<span class="rev-card-unit">%</span>`;
    const recSign = recDelta >= 0 ? '+' : '';
    const recTrendElem = document.getElementById('kpi-rec-trend');
    recTrendElem.textContent = `${recSign}${formatNumber(recDelta, 1)}% vs BM`;
    recTrendElem.className = `trend-pill ${recDelta >= 0 ? 'positive' : 'alert'}`;

    // Valuation Card
    document.getElementById('kpi-val-val').innerHTML = `$${formatNumber(totalValuation, 1)} <span class="rev-card-unit">M</span>`;

    // Risk Card
    document.getElementById('kpi-risk-val').innerHTML = `${highRiskCount.toLocaleString()} <span class="rev-card-unit">(${formatNumber(riskPct, 0)}%)</span>`;
    const riskTrendElem = document.getElementById('kpi-risk-trend');
    riskTrendElem.className = `trend-pill ${riskPct > 30 ? 'alert' : 'warning'}`;

    // Per Capita Card
    document.getElementById('kpi-percap-val').innerHTML = `${formatNumber(avgPerCapita, 1)} <span class="rev-card-unit">kg/person</span>`;
    document.getElementById('kpi-percap-trend').textContent = `${filtered.length}/${dataset.length} Nations`;

    // Sidebar status
    const matchPct = dataset.length > 0 ? (filtered.length / dataset.length) * 100 : 0;
    document.getElementById('feed-active-count').innerHTML = `${filtered.length.toLocaleString()} <span style="font-size:0.8rem; font-weight:500; color:var(--text-faint);">/ ${dataset.length.toLocaleString()} nations</span>`;
    document.getElementById('feed-coverage-val').textContent = `● ${formatNumber(matchPct, 1)}% Global Coverage Active`;
    document.getElementById('banner-scope-count').textContent = filtered.length.toLocaleString();
    document.getElementById('banner-scope-pct').textContent = `${formatNumber(matchPct, 1)}%`;
  }

  // 5. EXECUTIVE TAKEAWAYS
  function renderInsights(filtered) {
    if (filtered.length === 0) return;

    // 1. Largest Producer
    const topWaste = filtered.slice().sort((a, b) => b.Total_Plastic_Waste_MT - a.Total_Plastic_Waste_MT)[0];
    const totalWasteSum = filtered.reduce((acc, c) => acc + c.Total_Plastic_Waste_MT, 0);
    const topWasteShare = totalWasteSum > 0 ? (topWaste.Total_Plastic_Waste_MT / totalWasteSum) * 100 : 0;

    document.getElementById('insight-vol-main').textContent = `${topWaste.Country} • ${formatNumber(topWaste.Total_Plastic_Waste_MT, 2)} MT`;
    document.getElementById('insight-vol-sub').textContent = `Drives ${formatNumber(topWasteShare, 1)}% of current filtered waste footprint.`;

    // 2. Highest Recycling
    const topRec = filtered.slice().sort((a, b) => b.Recycling_Rate - a.Recycling_Rate)[0];
    document.getElementById('insight-rec-main').textContent = `${topRec.Country} • ${formatNumber(topRec.Recycling_Rate, 1)}% Recycled`;
    document.getElementById('insight-rec-sub').textContent = `Global benchmark average is ${formatNumber(BASELINE.recycling, 1)}%.`;

    // 3. Highest Per Capita
    const topPerCap = filtered.slice().sort((a, b) => b.Per_Capita_Waste_KG - a.Per_Capita_Waste_KG)[0];
    document.getElementById('insight-percap-main').textContent = `${topPerCap.Country} • ${formatNumber(topPerCap.Per_Capita_Waste_KG, 1)} kg`;
    document.getElementById('insight-percap-sub').textContent = `Global average is ${formatNumber(BASELINE.perCapita, 1)} kg/person.`;

    // 4. Dominant Stream
    const streamCounts = {};
    filtered.forEach(c => {
      streamCounts[c.Main_Sources] = (streamCounts[c.Main_Sources] || 0) + 1;
    });
    let dominantStream = 'N/A';
    let maxStreamCount = 0;
    for (const [stream, count] of Object.entries(streamCounts)) {
      if (count > maxStreamCount) {
        maxStreamCount = count;
        dominantStream = stream;
      }
    }
    const dominantShare = filtered.length > 0 ? (maxStreamCount / filtered.length) * 100 : 0;
    document.getElementById('insight-stream-main').textContent = dominantStream.replace(/_/g, ' ');
    document.getElementById('insight-stream-sub').textContent = `Primary stream across ${maxStreamCount} nations (${formatNumber(dominantShare, 1)}%).`;
  }

  // 6. PLOTLY CHARTS RENDERING
  function renderAllCharts(filtered) {
    renderCoastalDonut(filtered);
    renderMainSourcesChart(filtered);
    renderScatterChart(filtered);
    renderTopWasteChart(filtered);
    renderPerCapitaChart(filtered);
    renderRecyclingRatesChart(filtered);
    renderBenchmarkMatrix(filtered);
  }

  // Chart 1: Coastal Risk Donut
  function renderCoastalDonut(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-coastal-risk');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    const counts = {};
    RISK_ORDER.forEach(r => (counts[r] = 0));
    filtered.forEach(c => {
      if (counts[c.Coastal_Waste_Risk] !== undefined) counts[c.Coastal_Waste_Risk]++;
      else counts[c.Coastal_Waste_Risk] = 1;
    });

    const labels = [];
    const values = [];
    const colors = [];
    const customSample = [];

    RISK_ORDER.forEach(r => {
      if (counts[r] > 0) {
        labels.push(r.replace('_', ' '));
        values.push(counts[r]);
        colors.push(RISK_COLORS[r] || '#94A3B8');
        const samples = filtered
          .filter(c => c.Coastal_Waste_Risk === r)
          .slice(0, 6)
          .map(c => c.Country);
        customSample.push(samples.join(', ') + (counts[r] > 6 ? ', ...' : ''));
      }
    });

    const data = [
      {
        type: 'pie',
        labels: labels,
        values: values,
        hole: 0.64,
        marker: {
          colors: colors,
          line: { color: currentTheme === 'dark' ? '#0B0F19' : '#FFFFFF', width: 2.5 },
        },
        textinfo: 'label+percent',
        textfont: { size: 11, color: pTheme.font.color, family: pTheme.font.family },
        sort: false,
        customdata: customSample,
        hovertemplate:
          '<b>%{label} Risk</b><br>' +
          'Country Count: <b>%{value}</b><br>' +
          'Share: <b>%{percent}</b><br>' +
          'Nations: %{customdata}<extra></extra>',
      },
    ];

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: true,
      legend: { orientation: 'h', y: -0.15, x: 0.1 },
      margin: { t: 25, b: 40, l: 20, r: 20 },
      annotations: [
        {
          text: `<b style="font-size:20px;">${filtered.length}</b><br><span style="font-size:10px; color:${pTheme.font.color}; opacity:0.7;">NATIONS</span>`,
          x: 0.5,
          y: 0.5,
          font: { size: 15, family: pTheme.font.family, color: pTheme.font.color },
          showarrow: false,
        },
      ],
      height: 360,
    };

    Plotly.react(elem, data, layout, { responsive: true, displayModeBar: false });
  }

  // Chart 2: Main Sources Bar
  function renderMainSourcesChart(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-main-sources');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    const counts = {};
    filtered.forEach(c => {
      counts[c.Main_Sources] = (counts[c.Main_Sources] || 0) + 1;
    });

    const sortedSources = Object.entries(counts).sort((a, b) => a[1] - b[1]);
    const yLabels = sortedSources.map(s => s[0].replace(/_/g, ' '));
    const xVals = sortedSources.map(s => s[1]);
    const sharePcts = sortedSources.map(s => formatNumber((s[1] / filtered.length) * 100, 1));

    const data = [
      {
        type: 'bar',
        x: xVals,
        y: yLabels,
        orientation: 'h',
        marker: {
          color: xVals,
          colorscale: [
            [0, '#0E7490'],
            [0.5, '#06B6D4'],
            [1, '#67E8F9'],
          ],
          line: { color: '#A5F3FC', width: 1 },
        },
        text: xVals.map(v => v.toLocaleString()),
        textposition: 'outside',
        customdata: sharePcts,
        hovertemplate:
          '<b>%{y}</b><br>Nations: <b>%{x}</b><br>Proportion: <b>%{customdata}%</b><extra></extra>',
      },
    ];

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: false,
      margin: { t: 25, b: 35, l: 150, r: 40 },
      xaxis: {
        title: { text: 'Number of Countries', font: { size: 11 } },
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      yaxis: { gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      height: 360,
    };

    Plotly.react(elem, data, layout, { responsive: true, displayModeBar: false });
  }

  // Chart 3: Waste vs Recycling Scatter
  function renderScatterChart(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-scatter');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    const traces = [];
    RISK_ORDER.forEach(risk => {
      const cohort = filtered.filter(c => c.Coastal_Waste_Risk === risk);
      if (cohort.length === 0) return;

      traces.push({
        name: `${risk.replace('_', ' ')} Risk`,
        type: 'scatter',
        mode: 'markers',
        x: cohort.map(c => c.Total_Plastic_Waste_MT),
        y: cohort.map(c => c.Recycling_Rate),
        marker: {
          color: RISK_COLORS[risk],
          size: cohort.map(c => Math.max(8, Math.min(36, Math.sqrt(c.Per_Capita_Waste_KG) * 1.8))),
          opacity: 0.85,
          line: { color: '#FFFFFF', width: 1.2 },
        },
        customdata: cohort.map(c => [
          c.Country,
          formatNumber(c.Total_Plastic_Waste_MT, 2),
          formatNumber(c.Recycling_Rate, 1),
          formatNumber(c.Per_Capita_Waste_KG, 1),
          c.Main_Sources.replace(/_/g, ' '),
          c.Coastal_Waste_Risk.replace('_', ' '),
        ]),
        hovertemplate:
          '<b>%{customdata[0]}</b><br>' +
          'Total Plastic Waste: <b>%{customdata[1]} MT</b><br>' +
          'Recycling Margin: <b>%{customdata[2]}%</b><br>' +
          'Per-Capita Waste: <b>%{customdata[3]} kg/person</b><br>' +
          'Coastal Risk: <b>%{customdata[5]}</b><br>' +
          'Stream: %{customdata[4]}<extra></extra>',
      });
    });

    const maxRec = Math.max(...filtered.map(c => c.Recycling_Rate), 15);

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: true,
      legend: { orientation: 'h', y: 1.15, x: 0 },
      margin: { t: 40, b: 45, l: 55, r: 25 },
      xaxis: {
        title: {
          text: `Total Plastic Waste (MT)${scatterLogScale ? ' [Logarithmic Scale]' : ''}`,
          font: { size: 11 },
        },
        type: scatterLogScale ? 'log' : 'linear',
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      yaxis: {
        title: { text: 'Recycling Rate (%)', font: { size: 11 } },
        range: [0, Math.min(100, maxRec * 1.12)],
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      height: 420,
    };

    Plotly.react(elem, dataTraces(traces), layout, { responsive: true, displayModeBar: false });
  }

  function dataTraces(traces) {
    return traces;
  }

  // Chart 4: Top 10 Total Waste Bar
  function renderTopWasteChart(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-top-waste');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    const top10 = filtered
      .slice()
      .sort((a, b) => b.Total_Plastic_Waste_MT - a.Total_Plastic_Waste_MT)
      .slice(0, 10)
      .reverse();

    const data = [
      {
        type: 'bar',
        x: top10.map(c => c.Total_Plastic_Waste_MT),
        y: top10.map(c => c.Country),
        orientation: 'h',
        marker: {
          color: top10.map(c => c.Total_Plastic_Waste_MT),
          colorscale: [
            [0, '#4338CA'],
            [0.5, '#6366F1'],
            [1, '#8B5CF6'],
          ],
          line: { color: '#A5B4FC', width: 1 },
        },
        text: top10.map(c => `${formatNumber(c.Total_Plastic_Waste_MT, 2)} MT`),
        textposition: 'outside',
        customdata: top10.map(c => [
          formatNumber(c.Total_Plastic_Waste_MT, 2),
          formatNumber(c.Recycling_Rate, 1),
          formatNumber(c.Per_Capita_Waste_KG, 1),
          c.Coastal_Waste_Risk.replace('_', ' '),
          c.Main_Sources.replace(/_/g, ' '),
        ]),
        hovertemplate:
          '<b>%{y}</b><br>' +
          'Total Plastic Waste: <b>%{customdata[0]} MT</b><br>' +
          'Recycling Efficiency: %{customdata[1]}%<br>' +
          'Per-Capita Generation: %{customdata[2]} kg/person<br>' +
          'Coastal Risk: %{customdata[3]}<br>' +
          'Primary Stream: %{customdata[4]}<extra></extra>',
      },
    ];

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: false,
      margin: { t: 20, b: 35, l: 110, r: 70 },
      xaxis: {
        title: { text: 'Total Plastic Waste (MT)', font: { size: 11 } },
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      yaxis: { gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      height: 380,
    };

    Plotly.react(elem, data, layout, { responsive: true, displayModeBar: false });
  }

  // Chart 5: Top 10 Per Capita Bar
  function renderPerCapitaChart(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-per-capita');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    const top10 = filtered
      .slice()
      .sort((a, b) => b.Per_Capita_Waste_KG - a.Per_Capita_Waste_KG)
      .slice(0, 10)
      .reverse();

    const data = [
      {
        type: 'bar',
        x: top10.map(c => c.Per_Capita_Waste_KG),
        y: top10.map(c => c.Country),
        orientation: 'h',
        marker: {
          color: top10.map(c => c.Per_Capita_Waste_KG),
          colorscale: [
            [0, '#C2410C'],
            [0.5, '#F97316'],
            [1, '#FDBA74'],
          ],
          line: { color: '#FED7AA', width: 1 },
        },
        text: top10.map(c => `${formatNumber(c.Per_Capita_Waste_KG, 1)} kg`),
        textposition: 'outside',
        customdata: top10.map(c => [
          formatNumber(c.Per_Capita_Waste_KG, 1),
          formatNumber(c.Total_Plastic_Waste_MT, 2),
          formatNumber(c.Recycling_Rate, 1),
          c.Coastal_Waste_Risk.replace('_', ' '),
          c.Main_Sources.replace(/_/g, ' '),
        ]),
        hovertemplate:
          '<b>%{y}</b><br>' +
          'Per-Capita Waste: <b>%{customdata[0]} kg/person</b><br>' +
          'Total Plastic Waste: %{customdata[1]} MT<br>' +
          'Recycling Margin: %{customdata[2]}%<br>' +
          'Coastal Risk: %{customdata[3]}<br>' +
          'Primary Stream: %{customdata[4]}<extra></extra>',
      },
    ];

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: false,
      margin: { t: 20, b: 35, l: 110, r: 70 },
      xaxis: {
        title: { text: 'Per-Capita Plastic Waste (kg/person)', font: { size: 11 } },
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      yaxis: { gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      height: 380,
    };

    Plotly.react(elem, data, layout, { responsive: true, displayModeBar: false });
  }

  // Chart 6: Recycling Rates Sorted Bar
  function renderRecyclingRatesChart(filtered) {
    const pTheme = getPlotlyTheme();
    const elem = document.getElementById('chart-recycling-rates');
    if (!elem) return;

    if (filtered.length === 0) {
      Plotly.purge(elem);
      return;
    }

    let sorted = filtered.slice();
    if (recSortMode === 'highest') {
      sorted.sort((a, b) => b.Recycling_Rate - a.Recycling_Rate);
    } else {
      sorted.sort((a, b) => a.Recycling_Rate - b.Recycling_Rate);
    }

    if (recScope !== 'all') {
      sorted = sorted.slice(0, Number(recScope));
    }
    // Reverse for bottom-to-top horizontal bar chart display
    sorted.reverse();

    const data = [
      {
        type: 'bar',
        x: sorted.map(c => c.Recycling_Rate),
        y: sorted.map(c => c.Country),
        orientation: 'h',
        marker: {
          color: sorted.map(c => c.Recycling_Rate),
          colorscale: [
            [0, '#047857'],
            [0.5, '#10B981'],
            [1, '#34D399'],
          ],
          line: { color: '#6EE7B7', width: 1 },
        },
        text: sorted.map(c => `${formatNumber(c.Recycling_Rate, 1)}%`),
        textposition: 'outside',
        customdata: sorted.map(c => [
          formatNumber(c.Recycling_Rate, 1),
          formatNumber(c.Total_Plastic_Waste_MT, 2),
          formatNumber(c.Per_Capita_Waste_KG, 1),
          c.Coastal_Waste_Risk.replace('_', ' '),
          c.Main_Sources.replace(/_/g, ' '),
        ]),
        hovertemplate:
          '<b>%{y}</b><br>' +
          'Recycling Margin: <b>%{customdata[0]}%</b><br>' +
          'Total Plastic Waste: %{customdata[1]} MT<br>' +
          'Per-Capita Waste: %{customdata[2]} kg/person<br>' +
          'Coastal Risk: %{customdata[3]}<br>' +
          'Primary Stream: %{customdata[4]}<extra></extra>',
      },
    ];

    const chartHeight = Math.max(380, Math.min(850, sorted.length * 24 + 80));

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: false,
      margin: { t: 20, b: 35, l: 110, r: 60 },
      xaxis: {
        title: { text: 'Recycling Rate (%)', font: { size: 11 } },
        range: [0, Math.min(100, Math.max(...sorted.map(c => c.Recycling_Rate), 10) * 1.15)],
        gridcolor: pTheme.gridcolor,
        zerolinecolor: pTheme.zerolinecolor,
      },
      yaxis: { gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      height: chartHeight,
    };

    Plotly.react(elem, data, layout, { responsive: true, displayModeBar: false });
  }

  // Chart 7: Head-to-Head Benchmark Matrix
  function renderBenchmarkMatrix(filtered) {
    const elem = document.getElementById('chart-benchmark-cohort');
    if (!elem) return;

    const cohortList = dataset.filter(c => benchmarkCohort.includes(c.Country));
    if (cohortList.length < 2) {
      elem.innerHTML = '<p style="padding:1rem; color:var(--text-faint);">Select at least 2 nations to display benchmark comparison.</p>';
      return;
    }

    const pTheme = getPlotlyTheme();
    const countries = cohortList.map(c => c.Country);

    const trace1 = {
      x: countries,
      y: cohortList.map(c => c.Total_Plastic_Waste_MT),
      name: 'Total Waste (MT)',
      type: 'bar',
      xaxis: 'x1',
      yaxis: 'y1',
      marker: { color: '#6366F1', line: { color: '#A5B4FC', width: 1 } },
      text: cohortList.map(c => formatNumber(c.Total_Plastic_Waste_MT, 2)),
      textposition: 'outside',
      hovertemplate: '<b>%{x}</b><br>Total Waste: %{y:,.2f} MT<extra></extra>',
    };

    const trace2 = {
      x: countries,
      y: cohortList.map(c => c.Recycling_Rate),
      name: 'Recycling Margin (%)',
      type: 'bar',
      xaxis: 'x2',
      yaxis: 'y2',
      marker: { color: '#10B981', line: { color: '#6EE7B7', width: 1 } },
      text: cohortList.map(c => `${formatNumber(c.Recycling_Rate, 1)}%`),
      textposition: 'outside',
      hovertemplate: '<b>%{x}</b><br>Recycling Margin: %{y:.1f}%<extra></extra>',
    };

    const trace3 = {
      x: countries,
      y: cohortList.map(c => c.Per_Capita_Waste_KG),
      name: 'Per-Capita (kg)',
      type: 'bar',
      xaxis: 'x3',
      yaxis: 'y3',
      marker: { color: '#F59E0B', line: { color: '#FDE68A', width: 1 } },
      text: cohortList.map(c => formatNumber(c.Per_Capita_Waste_KG, 1)),
      textposition: 'outside',
      hovertemplate: '<b>%{x}</b><br>Per-Capita: %{y:,.1f} kg/person<extra></extra>',
    };

    const layout = {
      paper_bgcolor: pTheme.paper_bgcolor,
      plot_bgcolor: pTheme.plot_bgcolor,
      font: pTheme.font,
      showlegend: false,
      grid: { rows: 1, columns: 3, pattern: 'independent' },
      margin: { t: 40, b: 40, l: 45, r: 25 },
      xaxis1: { domain: [0, 0.29], gridcolor: pTheme.gridcolor },
      yaxis1: { title: 'MT', gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      xaxis2: { domain: [0.35, 0.64], gridcolor: pTheme.gridcolor },
      yaxis2: { title: 'Percent (%)', gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      xaxis3: { domain: [0.71, 1], gridcolor: pTheme.gridcolor },
      yaxis3: { title: 'kg / person', gridcolor: pTheme.gridcolor, zerolinecolor: pTheme.zerolinecolor },
      annotations: [
        { text: '<b>Total Plastic Waste (MT)</b>', x: 0.145, y: 1.12, xref: 'paper', yref: 'paper', showarrow: false, font: { size: 12, color: pTheme.font.color } },
        { text: '<b>Recycling Margin (%)</b>', x: 0.495, y: 1.12, xref: 'paper', yref: 'paper', showarrow: false, font: { size: 12, color: pTheme.font.color } },
        { text: '<b>Per-Capita Waste (kg/person)</b>', x: 0.855, y: 1.12, xref: 'paper', yref: 'paper', showarrow: false, font: { size: 12, color: pTheme.font.color } },
      ],
      height: 380,
    };

    Plotly.react(elem, [trace1, trace2, trace3], layout, { responsive: true, displayModeBar: false });

    // Render Benchmark Variance Table
    renderBenchmarkTable(cohortList);
  }

  function renderBenchmarkTable(cohortList) {
    const tbody = document.getElementById('benchmark-table-body');
    if (!tbody) return;

    tbody.innerHTML = cohortList
      .map(c => {
        const wasteDiff = ((c.Total_Plastic_Waste_MT - BASELINE.waste) / BASELINE.waste) * 100;
        const recDiff = c.Recycling_Rate - BASELINE.recycling;
        const perCapDiff = ((c.Per_Capita_Waste_KG - BASELINE.perCapita) / BASELINE.perCapita) * 100;
        const wasteSign = wasteDiff >= 0 ? '+' : '';
        const recSign = recDiff >= 0 ? '+' : '';
        const perCapSign = perCapDiff >= 0 ? '+' : '';

        return `
        <tr>
          <td><b>${c.Country}</b></td>
          <td>${formatNumber(c.Total_Plastic_Waste_MT, 2)} MT</td>
          <td style="color:${wasteDiff > 0 ? 'var(--rose)' : 'var(--emerald)'}; font-weight:700;">${wasteSign}${formatNumber(wasteDiff, 1)}%</td>
          <td>${formatNumber(c.Recycling_Rate, 1)}%</td>
          <td style="color:${recDiff >= 0 ? 'var(--emerald)' : 'var(--rose)'}; font-weight:700;">${recSign}${formatNumber(recDiff, 1)} pts</td>
          <td>${formatNumber(c.Per_Capita_Waste_KG, 1)} kg</td>
          <td style="color:${perCapDiff > 0 ? 'var(--rose)' : 'var(--emerald)'}; font-weight:700;">${perCapSign}${formatNumber(perCapDiff, 1)}%</td>
          <td>$${formatNumber(c.Material_Valuation_USD_M, 2)}M</td>
          <td><span class="tag-risk ${c.Coastal_Waste_Risk}">${c.Coastal_Waste_Risk.replace('_', ' ')}</span></td>
          <td>${c.Main_Sources.replace(/_/g, ' ')}</td>
        </tr>
      `;
      })
      .join('');
  }

  // 7. COUNTRY DOSSIER
  function renderCountryDossier() {
    const country = dataset.find(c => c.Country === dossierCountry) || dataset[0];
    if (!country) return;

    document.getElementById('dossier-country-name').textContent = country.Country;
    const badgeElem = document.getElementById('dossier-risk-badge');
    badgeElem.textContent = `${country.Coastal_Waste_Risk.replace('_', ' ')} Coastal Risk`;
    badgeElem.className = `profile-badge-pill ${country.Coastal_Waste_Risk}`;

    document.getElementById('dossier-stream-pill').textContent = `Sector: ${country.Main_Sources.replace(/_/g, ' ')}`;

    // Metric 1: Total Waste
    const wasteDiff = ((country.Total_Plastic_Waste_MT - BASELINE.waste) / BASELINE.waste) * 100;
    const wasteSign = wasteDiff >= 0 ? '+' : '';
    document.getElementById('dossier-waste-val').textContent = `${formatNumber(country.Total_Plastic_Waste_MT, 2)} MT`;
    const wasteVarElem = document.getElementById('dossier-waste-var');
    wasteVarElem.textContent = `${wasteSign}${formatNumber(wasteDiff, 1)}% vs global mean (${formatNumber(BASELINE.waste, 2)} MT)`;
    wasteVarElem.style.color = wasteDiff > 0 ? 'var(--rose)' : 'var(--emerald)';

    // Metric 2: Recycling
    const recDiff = country.Recycling_Rate - BASELINE.recycling;
    const recSign = recDiff >= 0 ? '+' : '';
    document.getElementById('dossier-rec-val').textContent = `${formatNumber(country.Recycling_Rate, 1)}%`;
    const recVarElem = document.getElementById('dossier-rec-var');
    recVarElem.textContent = `${recSign}${formatNumber(recDiff, 1)} pts vs global mean (${formatNumber(BASELINE.recycling, 1)}%)`;
    recVarElem.style.color = recDiff >= 0 ? 'var(--emerald)' : 'var(--rose)';

    // Metric 3: Per-Capita
    const perCapDiff = ((country.Per_Capita_Waste_KG - BASELINE.perCapita) / BASELINE.perCapita) * 100;
    const perCapSign = perCapDiff >= 0 ? '+' : '';
    document.getElementById('dossier-percap-val').textContent = `${formatNumber(country.Per_Capita_Waste_KG, 1)} kg`;
    const perCapVarElem = document.getElementById('dossier-percap-var');
    perCapVarElem.textContent = `${perCapSign}${formatNumber(perCapDiff, 1)}% vs global mean (${formatNumber(BASELINE.perCapita, 1)} kg)`;
    perCapVarElem.style.color = perCapDiff > 0 ? 'var(--rose)' : 'var(--emerald)';

    // Metric 4: Valuation
    document.getElementById('dossier-val-val').textContent = `$${formatNumber(country.Material_Valuation_USD_M, 2)} M`;
  }

  // 8. GLOBAL DATA LEDGER
  function renderLedger(filtered) {
    const tbody = document.getElementById('ledger-table-body');
    if (!tbody) return;

    let rows = filtered.slice();
    if (ledgerQuery) {
      rows = rows.filter(r => r.Country.toLowerCase().includes(ledgerQuery.toLowerCase()));
    }

    rows.sort((a, b) => {
      let valA = a[ledgerSortCol];
      let valB = b[ledgerSortCol];
      if (typeof valA === 'string') {
        return ledgerSortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return ledgerSortAsc ? valA - valB : valB - valA;
    });

    tbody.innerHTML = rows
      .map(c => `
      <tr>
        <td><b>${c.Country}</b></td>
        <td>${formatNumber(c.Total_Plastic_Waste_MT, 2)}</td>
        <td>${c.Main_Sources.replace(/_/g, ' ')}</td>
        <td>${formatNumber(c.Recycling_Rate, 1)}%</td>
        <td>${formatNumber(c.Per_Capita_Waste_KG, 1)}</td>
        <td><span class="tag-risk ${c.Coastal_Waste_Risk}">${c.Coastal_Waste_Risk.replace('_', ' ')}</span></td>
        <td>$${formatNumber(c.Material_Valuation_USD_M, 2)}M</td>
      </tr>
    `)
      .join('');
  }

  // 9. CSV DOWNLOAD EXPORTER
  function exportCSV(rows, filename) {
    const headers = [
      'Country',
      'Total_Plastic_Waste_MT',
      'Main_Sources',
      'Recycling_Rate',
      'Per_Capita_Waste_KG',
      'Coastal_Waste_Risk',
      'Material_Valuation_USD_M',
    ];

    let csvContent = '\uFEFF' + headers.join(',') + '\n';
    rows.forEach(r => {
      const line = [
        `"${r.Country}"`,
        r.Total_Plastic_Waste_MT,
        `"${r.Main_Sources}"`,
        r.Recycling_Rate,
        r.Per_Capita_Waste_KG,
        `"${r.Coastal_Waste_Risk}"`,
        formatNumber(r.Material_Valuation_USD_M, 2),
      ].join(',');
      csvContent += line + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // 10. SETUP & EVENT LISTENERS
  function setupUI() {
    // Theme Toggle
    const darkBtn = document.getElementById('theme-dark-btn');
    const lightBtn = document.getElementById('theme-light-btn');

    function applyTheme(theme) {
      currentTheme = theme;
      localStorage.setItem('revenue_os_theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
      if (theme === 'dark') {
        darkBtn.classList.add('active');
        lightBtn.classList.remove('active');
      } else {
        lightBtn.classList.add('active');
        darkBtn.classList.remove('active');
      }
      document.getElementById('header-mode-badge').textContent = `⚡ Mode: ${theme.toUpperCase()}`;
      updateAll();
    }

    darkBtn.addEventListener('click', () => applyTheme('dark'));
    lightBtn.addEventListener('click', () => applyTheme('light'));
    applyTheme(currentTheme);

    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab');
        const targetPane = document.getElementById(`tab-${targetId}`);
        if (targetPane) {
          targetPane.classList.add('active');
          activeTab = targetId;
          // Trigger Plotly relayout to fit newly visible container
          window.dispatchEvent(new Event('resize'));
        }
      });
    });

    // Populate Sidebar Nations select & chips
    const nationSelect = document.getElementById('nation-select');
    const sortedCountries = dataset.map(c => c.Country).sort();
    sortedCountries.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      nationSelect.appendChild(opt);
    });

    nationSelect.addEventListener('change', () => {
      const val = nationSelect.value;
      if (val && !filterNations.has(val)) {
        filterNations.add(val);
        renderNationChips();
        updateAll();
      }
      nationSelect.value = '';
    });

    function renderNationChips() {
      const wrap = document.getElementById('nation-chips-wrap');
      wrap.innerHTML = '';
      filterNations.forEach(nation => {
        const chip = document.createElement('span');
        chip.className = 'chip-tag';
        chip.innerHTML = `${nation} <span>&times;</span>`;
        chip.addEventListener('click', () => {
          filterNations.delete(nation);
          renderNationChips();
          updateAll();
        });
        wrap.appendChild(chip);
      });
    }

    // Populate Main Sources Filter
    const sourcesGrid = document.getElementById('sources-filter-grid');
    const uniqueSources = Array.from(new Set(dataset.map(c => c.Main_Sources))).sort();
    uniqueSources.forEach(s => {
      const label = document.createElement('label');
      label.className = 'custom-checkbox';
      label.innerHTML = `
        <input type="checkbox" value="${s}">
        <span>${s.replace(/_/g, ' ')}</span>
      `;
      const input = label.querySelector('input');
      input.addEventListener('change', () => {
        if (input.checked) filterSources.add(s);
        else filterSources.delete(s);
        updateAll();
      });
      sourcesGrid.appendChild(label);
    });

    // Coastal Risks Checkboxes
    document.querySelectorAll('.risk-filter-cb').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked) filterRisks.add(cb.value);
        else filterRisks.delete(cb.value);
        updateAll();
      });
    });

    // Search Input
    document.getElementById('sidebar-search').addEventListener('input', e => {
      filterSearch = e.target.value.trim();
      updateAll();
    });

    // Recycling Range Sliders
    const recMinSlider = document.getElementById('slider-rec-min');
    const recMaxSlider = document.getElementById('slider-rec-max');
    const recValDisp = document.getElementById('disp-rec-val');

    function handleRecChange() {
      let min = parseFloat(recMinSlider.value);
      let max = parseFloat(recMaxSlider.value);
      if (min > max) [min, max] = [max, min];
      filterRecMin = min;
      filterRecMax = max;
      recValDisp.textContent = `${min.toFixed(1)}% — ${max.toFixed(1)}%`;
      updateAll();
    }
    recMinSlider.addEventListener('input', handleRecChange);
    recMaxSlider.addEventListener('input', handleRecChange);

    // Waste Range Sliders
    const wasteMinSlider = document.getElementById('slider-waste-min');
    const wasteMaxSlider = document.getElementById('slider-waste-max');
    const wasteValDisp = document.getElementById('disp-waste-val');

    function handleWasteChange() {
      let min = parseFloat(wasteMinSlider.value);
      let max = parseFloat(wasteMaxSlider.value);
      if (min > max) [min, max] = [max, min];
      filterWasteMin = min;
      filterWasteMax = max;
      wasteValDisp.textContent = `${min.toFixed(2)} — ${max.toFixed(2)} MT`;
      updateAll();
    }
    wasteMinSlider.addEventListener('input', handleWasteChange);
    wasteMaxSlider.addEventListener('input', handleWasteChange);

    // Reset Parameters
    document.getElementById('btn-reset-filters').addEventListener('click', () => {
      filterSearch = '';
      document.getElementById('sidebar-search').value = '';
      filterNations.clear();
      renderNationChips();
      filterRisks.clear();
      document.querySelectorAll('.risk-filter-cb').forEach(cb => (cb.checked = false));
      filterSources.clear();
      sourcesGrid.querySelectorAll('input').forEach(cb => (cb.checked = false));

      recMinSlider.value = 0.1;
      recMaxSlider.value = 84.8;
      filterRecMin = 0.1;
      filterRecMax = 84.8;
      recValDisp.textContent = '0.1% — 84.8%';

      wasteMinSlider.value = 0.01;
      wasteMaxSlider.value = 59.08;
      filterWasteMin = 0.01;
      filterWasteMax = 59.08;
      wasteValDisp.textContent = '0.01 — 59.08 MT';

      updateAll();
    });

    // Scatter Log Scale Toggle
    document.getElementById('cb-scatter-log').addEventListener('change', e => {
      scatterLogScale = e.target.checked;
      renderScatterChart(getFilteredDataset());
    });

    // Recycling Chart Controls
    document.getElementById('rec-sort-select').addEventListener('change', e => {
      recSortMode = e.target.value;
      renderRecyclingRatesChart(getFilteredDataset());
    });

    document.getElementById('rec-scope-select').addEventListener('change', e => {
      recScope = e.target.value;
      renderRecyclingRatesChart(getFilteredDataset());
    });

    // Benchmark Multiselect
    const bmSelect = document.getElementById('benchmark-select');
    sortedCountries.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      bmSelect.appendChild(opt);
    });

    bmSelect.addEventListener('change', () => {
      const val = bmSelect.value;
      if (val && !benchmarkCohort.includes(val) && benchmarkCohort.length < 8) {
        benchmarkCohort.push(val);
        renderBenchmarkChips();
        renderBenchmarkMatrix(getFilteredDataset());
      }
      bmSelect.value = '';
    });

    function renderBenchmarkChips() {
      const wrap = document.getElementById('benchmark-chips-wrap');
      wrap.innerHTML = '';
      benchmarkCohort.forEach(c => {
        const chip = document.createElement('span');
        chip.className = 'chip-tag';
        chip.innerHTML = `${c} <span>&times;</span>`;
        chip.addEventListener('click', () => {
          if (benchmarkCohort.length > 2) {
            benchmarkCohort = benchmarkCohort.filter(item => item !== c);
            renderBenchmarkChips();
            renderBenchmarkMatrix(getFilteredDataset());
          }
        });
        wrap.appendChild(chip);
      });
    }
    renderBenchmarkChips();

    // Benchmark Download CSV
    document.getElementById('btn-download-benchmark').addEventListener('click', () => {
      const cohortList = dataset.filter(c => benchmarkCohort.includes(c.Country));
      exportCSV(cohortList, 'revenue_os_country_benchmark.csv');
    });

    // Country Dossier Selector
    const dossierSelect = document.getElementById('dossier-select');
    sortedCountries.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      if (c === dossierCountry) opt.selected = true;
      dossierSelect.appendChild(opt);
    });
    dossierSelect.addEventListener('change', e => {
      dossierCountry = e.target.value;
      renderCountryDossier();
    });

    // Ledger Explorer Controls
    document.getElementById('ledger-search').addEventListener('input', e => {
      ledgerQuery = e.target.value.trim();
      renderLedger(getFilteredDataset());
    });

    document.getElementById('ledger-sort-col').addEventListener('change', e => {
      ledgerSortCol = e.target.value;
      renderLedger(getFilteredDataset());
    });

    document.getElementById('ledger-sort-order').addEventListener('change', e => {
      ledgerSortAsc = e.target.value === 'asc';
      renderLedger(getFilteredDataset());
    });

    document.getElementById('btn-download-ledger').addEventListener('click', () => {
      exportCSV(getFilteredDataset(), 'revenue_os_plastic_waste_ledger.csv');
    });

    // Mobile Sidebar Toggle
    const mobileToggle = document.getElementById('mobile-nav-toggle');
    const sidebar = document.querySelector('.sidebar');
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // 11. ORCHESTRATE ALL
  function updateAll() {
    const filtered = getFilteredDataset();
    renderHeroKPIs(filtered);
    renderInsights(filtered);
    renderAllCharts(filtered);
    renderCountryDossier();
    renderLedger(filtered);
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    setupUI();
    updateAll();
  });
})();
