import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className="text--center">
          <Heading as="h1" className="hero__title">
            Physical AI & Humanoid Robotics
          </Heading>
          <p className="hero__subtitle">
            A complete hands-on textbook bridging AI systems with the physical world using ROS 2, Simulation, NVIDIA Isaac, and Vision-Language-Action models.
          </p>
          <div className={styles.buttons}>
            <Link
              className="button button--secondary button--lg"
              to="/docs/module-1-ros2">
              Start Module 1 →
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

type ModuleItem = {
  title: string;
  description: string;
  to: string;
};

const ModuleList: ModuleItem[] = [
  {
    title: 'Module 1: ROS 2',
    description: 'Learn ROS 2 fundamentals, nodes, topics, services, and actions for robot communication and control.',
    to: '/docs/module-1-ros2',
  },
  {
    title: 'Module 2: Simulation',
    description: 'Master digital twin technologies with Gazebo and Unity for robot simulation and testing.',
    to: '/docs/module-2-simulation',
  },
  {
    title: 'Module 3: Isaac',
    description: 'Build AI-powered robot brains using NVIDIA Isaac for perception and decision making.',
    to: '/docs/module-3-isaac',
  },
  {
    title: 'Module 4: VLA',
    description: 'Implement Vision-Language-Action models for advanced human-robot interaction.',
    to: '/docs/module-4-vla',
  },
];

function ModuleCard({title, description, to}: ModuleItem) {
  return (
    <div className="col col--3 margin-bottom--lg">
      <div className="card">
        <div className="card__header">
          <h3>{title}</h3>
        </div>
        <div className="card__body">
          <p>{description}</p>
        </div>
        <div className="card__footer">
          <Link className="button button--primary" to={to}>
            Explore
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics`}
      description="A complete hands-on textbook bridging AI systems with the physical world using ROS 2, Simulation, NVIDIA Isaac, and Vision-Language-Action models.">
      <HomepageHeader />
      <main>
        <section className={styles.modules}>
          <div className="container padding-vert--lg">
            <div className="row">
              {ModuleList.map((module, idx) => (
                <ModuleCard key={idx} {...module} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
