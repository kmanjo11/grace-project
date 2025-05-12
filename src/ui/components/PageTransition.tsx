import React, { ReactNode, ErrorInfo } from 'react';
import '../styles/transitions.css';

interface ErrorBoundaryState {
  hasError: boolean;
}

class TransitionErrorBoundary extends React.Component<{children: ReactNode}, ErrorBoundaryState> {
  constructor(props: {children: ReactNode}) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Transition Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div className="error-fallback">Page failed to load</div>;
    }

    return this.props.children;
  }
}

interface PageTransitionProps {
  children: ReactNode;
  key: string;
}

// Simple transition wrapper that doesn't use CSSTransition
export const PageTransition: React.FC<PageTransitionProps> = ({ children, key }) => (
  <TransitionErrorBoundary>
    <div key={key} className="page-enter page-enter-active">
      {children}
    </div>
  </TransitionErrorBoundary>
);
