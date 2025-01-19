import styles from "./styles/loadingAnimBlock.module.css";

interface LoadingAnimBlockProps {
  isVisible: boolean;
  children: React.ReactNode;
}

export function LoadingAnimBlock({
  isVisible,
  children,
}: LoadingAnimBlockProps) {
  return (
    <div className={styles.loader_container}>
      {isVisible ? <div className={styles.loader}></div> : children}
    </div>
  );
}
