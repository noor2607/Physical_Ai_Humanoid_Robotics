import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Embodied Intelligence • ROS 2 • Simulation • Humanoid AI',
  favicon: 'img/robot-icon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://physical-ai-course.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'physical-ai-course', // Usually your GitHub org/user name.
  projectName: 'physical-ai-humanoid-course', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          sidebarCollapsible: true,
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI & Humanoid Robotics Logo',
        src: 'img/book-icon.png', // Placeholder - will be replaced with emoji
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'courseSidebar',
          position: 'left',
          label: 'Course Content',
        },
        {
          type: 'dropdown',
          label: 'Modules',
          position: 'left',
          items: [
            {
              label: 'Module 1: ROS 2',
              to: '/docs/module-1-ros2',
            },
            {
              label: 'Module 2: Simulation',
              to: '/docs/module-2-simulation',
            },
            {
              label: 'Module 3: Isaac',
              to: '/docs/module-3-isaac',
            },
            {
              label: 'Module 4: VLA',
              to: '/docs/module-4-vla',
            },
          ],
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/physical-ai-course/physical-ai-humanoid-course',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Course Modules',
          items: [
            {
              label: 'Module 1: ROS 2 Fundamentals',
              to: '/docs/module-1-ros2',
            },
            {
              label: 'Module 2: Digital Twin (Gazebo & Unity)',
              to: '/docs/module-2-simulation',
            },
            {
              label: 'Module 3: AI-Robot Brain (NVIDIA Isaac)',
              to: '/docs/module-3-isaac',
            },
            {
              label: 'Module 4: Vision-Language-Action (VLA)',
              to: '/docs/module-4-vla',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Module 1 Exercises',
              to: '/docs/exercises',
            },
            {
              label: 'Simulations',
              to: '/docs/category/simulations',
            },
            {
              label: 'API Reference',
              to: '/docs/api-reference',
            },
          ],
        },
        {
          title: 'Accessibility',
          items: [
            {
              label: 'Accessibility Statement',
              to: '/docs/accessibility',
            },
            {
              label: 'Screen Reader Guide',
              to: '/docs/screen-reader-guide',
            },
            {
              label: 'Keyboard Navigation',
              to: '/docs/keyboard-navigation',
            },
          ],
        },
        {
          title: 'Collaboration',
          items: [
            {
              label: 'Collaborative Learning',
              to: '/docs/collaborative-learning',
            },
            {
              label: 'Discussion Forums',
              href: 'https://discord.gg/physical-ai',
            },
            {
              label: 'Peer Review System',
              to: '/docs/collaborative-learning#peer-review-system',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/physical-ai',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/physical-ai-course/physical-ai-humanoid-course',
            },
            {
              label: 'Documentation',
              href: 'https://docs.physical-ai-course.com',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Course. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
