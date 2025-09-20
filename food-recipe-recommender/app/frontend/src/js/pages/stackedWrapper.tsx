import { Navbar, NavbarItem, NavbarSection, NavbarSpacer } from '../components/navbar'
import { Sidebar, SidebarBody, SidebarHeader, SidebarItem, SidebarSection } from '../components/sidebar'
import { StackedLayout } from '../components/stacked-layout'
import { ArrowRightStartOnRectangleIcon } from '@heroicons/react/16/solid'
import { Button } from '../components/button'
import { Heading } from '../components/heading'
import type { ReactNode } from 'react'

const navItems = [
  { label: 'Search', url: '/' },
  { label: 'Recommendations', url: '/recommendations' },
  { label: 'Saved Recipes', url: '/saved-recipes' },
]

export default function StackedWrapper({ children }: { children?: ReactNode }) {
  const handleSignOut = async () => {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      });
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
      // Force redirect anyway
      window.location.href = '/login';
    }
  };

  return (
    <StackedLayout
      navbar={
        <Navbar>
          <NavbarSection>
            <NavbarItem>
              <Heading level={2} className="text-lg font-semibold">Recipe Recommender</Heading>
            </NavbarItem>
          </NavbarSection>
          <NavbarSection className="max-lg:hidden">
            {navItems.map(({ label, url }) => (
              <NavbarItem key={label} href={url}>
                {label}
              </NavbarItem>
            ))}
          </NavbarSection>
          <NavbarSpacer />
          <NavbarSection>
            <Button
              color="gray"
              onClick={handleSignOut}
              className="flex items-center gap-2"
            >
              <ArrowRightStartOnRectangleIcon className="w-4 h-4" />
              Sign Out
            </Button>
          </NavbarSection>
        </Navbar>
      }
      sidebar={
        <Sidebar>
          <SidebarHeader>
            <SidebarItem>
              <Heading level={3} className="text-base font-semibold px-2">Recipe Recommender</Heading>
            </SidebarItem>
          </SidebarHeader>
          <SidebarBody>
            <SidebarSection>
              {navItems.map(({ label, url }) => (
                <SidebarItem key={label} href={url}>
                  {label}
                </SidebarItem>
              ))}
            </SidebarSection>
            <SidebarSection className="mt-auto">
              <SidebarItem as="button" onClick={handleSignOut} className="flex items-center gap-2">
                <ArrowRightStartOnRectangleIcon className="w-4 h-4" />
                Sign Out
              </SidebarItem>
            </SidebarSection>
          </SidebarBody>
        </Sidebar>
      }
    >
      {children}
    </StackedLayout>
  )
}