%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%          Document class for Knowdive internal reports
%
%  author: Pierre Andrews (andrews@disi.unitn.it)
%  version: 1.0
%  release: 11/05/2009
%
%  Usage Example:
% \documentclass{knowdive}

% \title{This is a test}
% \docdata{08.10.27.v00.r02}

% \author{Pierre Andrews \and Alice Bob \and Mr Tee}

% \revisionhistory{
%       \revision{0.1}{26.09.80}{Pierre Andrews}{Some changes}
%       \revision{0.2}{26.09.80}{Pierre Andrews}{Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eget urna mauris. Phasellus interdum semper ligula ac dictum. Donec ut.}
% }

% \internalreferences{
% \reference{ref1}
% \reference{ref2}
% }

% \begin{document}
% \maketitle
%
%  Put the usual latex stuff here
%
% \end{document}
%
% Special Preamble Commands:
%  - \author is the usual author macro, you can have multiple authors
%     by separating them by \and
%  - \docdata is the identifier of the document
%  - \revisionhistory defines a block of revisions of the document, it
%  should contain \revision items
%    * \revision{a}{b}{c}{d} defines a revion. (a) is the version
%    number, (b) is a data, (c) is the author name, (d) is a
%    description. Can be multiline
%  - \internalreferences defines a block of references to internal
%  documents, it should contain \reference items
%     * \reference is a reference item, it takes one parameter that
%     should be the formated reference.
% 
% you have to call \maketitle after \begin{document} to create the
% title page.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\ProvidesClass{knowdive}




\LoadClass[titlepage]{article}

\usepackage{fontspec}
\setsansfont{Arial}
\setmainfont{Arial}
\large

\RequirePackage{graphicx}
\RequirePackage{tabularx}


\RequirePackage[left=2cm,top=2cm,right=2cm]{geometry}

\RequirePackage{setspace}
\onehalfspacing

\def\docdata#1{\gdef\@docdata{#1}}
\def\revisionhistory#1{\gdef\@revisionhistory{\noindent{\normalfont\Large\bfseries
      Revision History:}\\[.5cm]\begin{revisionhistoryX} #1 \end{revisionhistoryX}}}
\def\internalreferences#1{\gdef\@internalreferences{{\normalfont\Large\bfseries
      References to existing KnowDive internal reports:}\\\begin{itemize}#1\end{itemize}}}

\def\and{\\&}

\def\@title{}
\def\@author{}
\def\@docdata{\today}
\def\@revisionhistory{}
\def\@internalreferences{}

\newenvironment{revisionhistoryX}{
\singlespacing
  \tabularx{\textwidth}{|l|l|l|X|}
    \hline
    \textbf{Revision}&\textbf{Date}&\textbf{Author}&\textbf{Description of Changes}\\\hline
}{
  \endtabularx
\doublespacing
}

\newcommand{\revision}[4]{#1\protect&#2\protect&#3\protect&#4\\\hline}

\newcommand{\reference}[1]{\protect\item #1}


\setcounter{secnumdepth}{4}
\pagenumbering{arabic}

\renewcommand{\contentsname}{Index:}


\def\maketitle{\begin{titlepage}%
\includegraphics[width=18cm]{knowDiveUNITN}\\%
\begin{center}%
% Upper part of the page
 \textsc{Dipartimento di Ingegneria e Scienza dell’Informazione}\\[.5cm]% 
 \textsc{\Large -- KnowDive Group --}\\[0.5cm]% 
% % Title
\vfill%
{ \Huge \bfseries\@title}\\[1.5cm]%
\hrulefill\\[3.5cm]%
 \begin{tabular*}{\textwidth}{p{.5\textwidth}p{.5\textwidth}}
   Document Data:\hfill&Reference Persons:\\\hline%
\@docdata&\@author \\%
\end{tabular*}%
 \end{center}%
\vfill%
\copyright\ \number\year ~University of Trento\\%
Trento, Italy\\[.5cm]%
%
\begin{singlespace}
  \small{\noindent KnowDive (internal) reports are for internal only use within
    the KnowDive Group. They describe preliminary or instrumental work
    which should not be disclosed outside the group. KnowDive reports
    cannot be mentioned or cited by documents which are not KnowDive
    reports. KnowDive reports are the result of the collaborative work
    of members of the KnowDive group. The people whose names are in
    this page cannot be taken to be the authors of this report, but
    only the people who can better provide detailed information about
    its contents. Official, citable material produced by the KnowDive
    group may take any of the official Academic forms, for instance:
    Master and PhD theses, DISI technical reports, papers in
    conferences and journals, or books.}
\end{singlespace}

\noindent
\includegraphics[width=1.0\linewidth,height=45pt]{Knowdive_color_bar}
%
\newpage%
\thispagestyle{plain}
\tableofcontents%
\vfill%
\@revisionhistory\\[1cm]%
%\@internalreferences%
\setcounter{page}{0}%
\end{titlepage}%
}
