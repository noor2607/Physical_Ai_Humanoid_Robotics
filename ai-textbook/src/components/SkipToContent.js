import React from 'react';
import clsx from 'clsx';
import styles from './SkipToContent.module.css';

const SkipToContent = () => {
  const handleSkip = (e) => {
    // Skip to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
      e.preventDefault();
      mainContent.focus();
      window.scrollTo(0, 0);
    }
  };

  return (
    <a
      href="#main"
      className={styles.skipLink}
      onClick={handleSkip}
    >
      Skip to main content
    </a>
  );
};

export default SkipToContent;