import React from 'react';
import OriginalNavbar from '@theme-original/Navbar';

export default function Navbar(props) {
  return (
    <>
      <div className="fixed top-0 right-4 z-50 mt-2">
      </div>
      <OriginalNavbar {...props} />
    </>
  );
}