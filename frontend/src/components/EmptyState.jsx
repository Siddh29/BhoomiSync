import {FolderSearch} from 'lucide-react';
export default function EmptyState({title='No completed results',description='Run harmonization to build a master layer and its review evidence.',children}) {
  return <div className="empty-state"><FolderSearch aria-hidden="true"/><h3>{title}</h3><p>{description}</p>{children}</div>;
}
