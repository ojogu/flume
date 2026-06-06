import { createBrowserRouter } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { BotPage } from '@/pages/BotPage'
import { PricingPage } from '@/pages/PricingPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/bot',
    element: <BotPage />,
  },
  {
    path: '/pricing',
    element: <PricingPage />,
  },
])