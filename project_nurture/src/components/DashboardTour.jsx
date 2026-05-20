import { Button } from '@chakra-ui/react';
import { driver } from 'driver.js';
import 'driver.js/dist/driver.css';
import { FiInfo } from 'react-icons/fi';

const tourSteps = [
  {
    element: '[data-tour="dashboard-guide"]',
    popover: {
      title: 'Dashboard context',
      description:
        'This section defines the data source, map behavior, filters, priority ranking, and privacy limits before the dashboard is used.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="dashboard-map"]',
    popover: {
      title: 'Mapped DHS clusters',
      description:
        'The map shows weighted aggregate indicators around displaced DHS survey cluster points, not exact household or case locations.',
      side: 'right',
      align: 'start',
    },
  },
  {
    element: '[data-tour="map-layer-control"]',
    popover: {
      title: 'Map layer modes',
      description:
        'Switch between cluster bubbles, a smoothed heat layer, or both. The heat layer is useful for scanning broad patterns, while bubbles retain sample context.',
      side: 'left',
      align: 'start',
    },
  },
  {
    element: '[data-tour="indicator-select"]',
    popover: {
      title: 'Map indicator',
      description:
        'Choose the nutrition indicator that drives the map colors, top clusters, and priority ranking.',
      side: 'left',
      align: 'start',
    },
  },
  {
    element: '[data-tour="demographic-filters"]',
    popover: {
      title: 'Demographic filters',
      description:
        'Filter the local aggregate by geography, residence, sex, wealth, and age band to inspect narrower DHS child nutrition cuts.',
      side: 'left',
      align: 'start',
    },
  },
  {
    element: '[data-tour="priority-tab"]',
    popover: {
      title: 'Priority areas',
      description:
        'The Priority tab ranks areas by combining the selected indicator with mapped survey sample size, so high rates are not read without context.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="privacy-note"]',
    popover: {
      title: 'Local data boundary',
      description:
        'The generated JSON comes from restricted DHS microdata and should remain local. Public views should use aggregate summaries only.',
      side: 'top',
      align: 'start',
    },
  },
];

const DashboardTour = () => {
  const startTour = () => {
    const availableSteps = tourSteps.filter(step => document.querySelector(step.element));

    if (!availableSteps.length) return;

    driver({
      allowClose: true,
      animate: true,
      doneBtnText: 'Done',
      nextBtnText: 'Next',
      popoverClass: 'dashboard-tour-popover',
      prevBtnText: 'Back',
      progressText: '{{current}} of {{total}}',
      showButtons: ['next', 'previous', 'close'],
      showProgress: true,
      stagePadding: 8,
      steps: availableSteps,
    }).drive();
  };

  return (
    <>
      <style>
        {`
          .dashboard-tour-popover {
            background: var(--chakra-colors-app-surface);
            color: var(--chakra-colors-app-text);
            border-radius: 8px;
            border: 1px solid var(--chakra-colors-app-borderStrong);
            box-shadow: 0 18px 46px rgba(15, 23, 42, 0.22);
          }

          .dashboard-tour-popover .driver-popover-title {
            font-size: 16px;
            line-height: 1.25;
          }

          .dashboard-tour-popover .driver-popover-description {
            color: var(--chakra-colors-app-muted);
            line-height: 1.5;
          }

          .dashboard-tour-popover .driver-popover-next-btn,
          .dashboard-tour-popover .driver-popover-prev-btn {
            border: 0 !important;
            border-radius: 6px;
            box-shadow: none !important;
            font-weight: 700;
            padding: 6px 10px;
            text-shadow: none !important;
            transition: background-color 120ms ease, color 120ms ease, opacity 120ms ease;
          }

          .dashboard-tour-popover .driver-popover-next-btn:not(:disabled) {
            background: #0f766e !important;
            color: #ffffff !important;
          }

          .dashboard-tour-popover .driver-popover-next-btn:not(:disabled):hover,
          .dashboard-tour-popover .driver-popover-next-btn:not(:disabled):focus {
            background: #115e59 !important;
            color: #ffffff !important;
          }

          .dashboard-tour-popover .driver-popover-prev-btn:not(:disabled) {
            background: var(--chakra-colors-app-surfaceMuted) !important;
            color: var(--chakra-colors-app-text) !important;
          }

          .dashboard-tour-popover .driver-popover-prev-btn:not(:disabled):hover,
          .dashboard-tour-popover .driver-popover-prev-btn:not(:disabled):focus {
            background: var(--chakra-colors-app-borderStrong) !important;
            color: var(--chakra-colors-app-text) !important;
          }

          .dashboard-tour-popover .driver-popover-next-btn:disabled,
          .dashboard-tour-popover .driver-popover-prev-btn:disabled {
            background: var(--chakra-colors-app-surfaceMuted) !important;
            color: var(--chakra-colors-app-subtle) !important;
            cursor: not-allowed;
            opacity: 0.72;
          }
        `}
      </style>
      <Button leftIcon={<FiInfo />} onClick={startTour} size="sm" colorScheme="teal">
        Start tour
      </Button>
    </>
  );
};

export default DashboardTour;
