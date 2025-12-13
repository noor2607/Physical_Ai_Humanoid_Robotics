import React from 'react';
import Layout from '@theme-original/Layout';
import SkipToContent from '@site/src/components/SkipToContent';

export default function LayoutWrapper(props) {
  return (
    <>
      <SkipToContent />
      <Layout {...props}>
        <main id="main" tabIndex="-1" style={{ outline: 'none' }}>
          {props.children}
        </main>
      </Layout>
    </>
  );
}