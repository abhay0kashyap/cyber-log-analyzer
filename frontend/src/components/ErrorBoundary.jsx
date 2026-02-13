import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-soc-bg p-8 text-sm text-[#ff6a6a]">
          UI render error detected. Reload to recover.
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
