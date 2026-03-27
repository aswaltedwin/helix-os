declare module 'react' {
  export type ReactNode = any;
  export type ReactElement = any;
  export default any;
}

declare module 'react-dom' {
  export default any;
}

declare module 'next' {
  export type Metadata = any;
}

declare module 'next/link' {
  export default any;
}

declare module 'next/navigation' {
  export function usePathname(): string;
  export function useRouter(): any;
}

declare module 'next/server' {
  export class NextResponse {
    static json(body: any, init?: any): any;
  }
}

declare module 'next/font/google' {
  export function Inter(options: any): any;
}

declare module 'lucide-react' {
  export const Users: any;
  export const Activity: any;
  export const FileText: any;
  export const Box: any;
}

declare module 'clsx' {
  export type ClassValue = any;
  export function clsx(...inputs: any[]): string;
}

declare module 'tailwind-merge' {
  export function twMerge(...inputs: any[]): string;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare var process: {
  env: {
    [key: string]: string | undefined;
  };
};
