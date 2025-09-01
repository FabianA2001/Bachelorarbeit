%%
%% This is file `tubsposter.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% ../tubsvers.inc  (with options: `default,extra')
%% tubsdoc.dtx  (with options: `class,poster,head')
%% tubsdoc.dtx  (with options: `class,poster,option')
%% tubsfont.dtx  (with options: `class,poster,option')
%% tubsposter.dtx  (with options: `class,poster,option')
%% tubsdoc.dtx  (with options: `class,poster,execoption')
%% tubsposter.dtx  (with options: `class,poster,execoption')
%% tubsdoc.dtx  (with options: `class,poster,body')
%% tubsfont.dtx  (with options: `class,poster,body')
%% tubsposter.dtx  (with options: `class,poster,body')
%% 
%% This is a generated file.
%% 
%% Copyright (C) 2011 by Enrico Jörns
%% 
%% This file may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either
%% version 1.2 of this license or (at your option) any later
%% version. The latest version of this license is in:
%% 
%%   http://www.latex-project.org/lppl.txt
%% 
%% and version 1.2 or later is part of all distributions of
%% LaTeX version 1999/12/01 or later.
%% 
\RequirePackage{ifthen}
\RequirePackage{scrlfile}%TODO: KOMA-Check?
\RequirePackage{etoolbox}%
\begingroup
  \makeatletter
  \ifx\tubslatexVersion\undefined
    \newcommand*{\check@tubslatexVersion}[1]{%
      \gdef\tubslatexVersion{#1}%
    }%
  \else
    \newcommand*{\check@tubslatexVersion}[1]{%
      \def\@tempa{#1}%
      \ifx\tubslatexVersion\@tempa\else
        \@latex@warning@no@line{%
          \noexpand\tubslatexVersion\space is
          `\tubslatexVersion',\MessageBreak
          but `#1' was expected!\MessageBreak
          You should not use classes, packages or files
          from\MessageBreak
          different tubslatex versions%
        }%
      \fi
    }
  \fi
  \check@tubslatexVersion{2024/02/22 v1.3.5-r140 tubslatex}%
\endgroup
\providecommand{\tubslatex}{tubs\LaTeX}
\AfterPackage*{ucs}{%
  \pretocmd{\author}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
  \pretocmd{\title}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
}
\AtBeginDocument{
  \@ifpackageloaded{hyperref}{%
    \@ifundefined{inputencodingname}{}{%
      \hypersetup{
        pdftitle = {\@title},
        pdfauthor = {\@author},
        pdfcreator = {\tubslatexVersion}
      }
    }
  }{}
}
\RequirePackage{ifthen}
\newcommand*{\tubsClassName}{%
  tubsposter%
}
\newcommand*{\BaseClass}{%
  scrartcl%
}
\NeedsTeXFormat{LaTeX2e}[1999/12/01]
\ProvidesClass{\tubsClassName}[\tubslatexVersion\space document class (\BaseClass)]
\newcommand*{\@fsfbs@sub}{}
\RequirePackage{xkeyval}%
\DeclareOptionX{mono}{%
  \PassOptionsToPackage{mono}{tubslogo}
  \PassOptionsToPackage{mono}{tubsflowfram}
}
\DeclareOptionX{cmyk}{%
  \PassOptionsToPackage{cmyk}{tubscolors}
  \PassOptionsToPackage{cmyk}{tubslogo}
}
\DeclareOptionX{rgb}{%
  \PassOptionsToPackage{rgb}{tubscolors}
  \PassOptionsToPackage{rgb}{tubslogo}
}
\DeclareOptionX{landscape}{%
  \PassOptionsToPackage{landscape}{tubstypearea}
  \PassOptionsToClass{landscape}{\BaseClass}
}
\DeclareOptionX{paperwidth}{%
  \PassOptionsToPackage{paperwidth=#1}{tubstypearea}
}
\DeclareOptionX{paperheight}{%
  \PassOptionsToPackage{paperheight=#1}{tubstypearea}
}
\DeclareOptionX{oneside}{%
\setkeys{\tubsClassName.cls}{twoside=false}
}
\DeclareOptionX{marginleft}{%
  \PassOptionsToPackage{marginleft}{tubstypearea}
}
\DeclareOptionX{marginright}{%
  \PassOptionsToPackage{marginright}{tubstypearea}
}
\DeclareOptionX{extramargin}{%
  \PassOptionsToPackage{extramargin}{tubstypearea}
}
\DeclareOptionX{bcor}{%
  \PassOptionsToPackage{bcor=#1}{tubstypearea}
}
\def\tubs@opt@paper{}
\newcommand{\@fsfb@prefix}{}
\DeclareOptionX{a6paper}{%
  \def\tubs@opt@paper{a6paper}
}
\DeclareOptionX{langpaper}{%
  \renewcommand{\@fsfb@prefix}{tubslang}
  \PassOptionsToClass{fontsize=9pt}{\BaseClass}
  \def\tubs@opt@paper{langpaper}
}
\DeclareOptionX{a5paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa5}
  \PassOptionsToClass{fontsize=9pt}{\BaseClass}
  \def\tubs@opt@paper{a5paper}
}
\DeclareOptionX{a4paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa4}
  \PassOptionsToClass{fontsize=11pt}{\BaseClass}
  \def\tubs@opt@paper{a4paper}
}
\DeclareOptionX{a3paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa3}
  \PassOptionsToClass{fontsize=13pt}{\BaseClass}
  \def\tubs@opt@paper{a3paper}
}
\DeclareOptionX{a2paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa2}
  \PassOptionsToClass{fontsize=18pt}{\BaseClass}
  \def\tubs@opt@paper{a2paper}
}
\DeclareOptionX{a1paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa1}
  \PassOptionsToClass{fontsize=25pt}{\BaseClass}
  \def\tubs@opt@paper{a1paper}
}
\DeclareOptionX{a0paper}{%
  \renewcommand{\@fsfb@prefix}{tubsa0}
  \PassOptionsToClass{fontsize=40pt}{\BaseClass}
  \def\tubs@opt@paper{a0paper}
}
\DeclareOptionX{backend}{%
  \if#1{flow}
    \def\tubs@opt@backend{flowfram}
  \fi
  \ifx#1{pgf}
    \def\tubs@opt@backend{pgf}
  \fi
  \ifthenelse{\equal{#1}{base}}{%
    \def\tubs@opt@backend{base}
  }{}
  \ifthenelse{\equal{#1}{flow}}{%
    \def\tubs@opt@backend{flowfram}
  }{}
  \ifthenelse{\equal{#1}{pgf}}{%
    \def\tubs@opt@backend{pgf}
  }{}
}
\DeclareOptionX{sender}{%
  \PassOptionsToPackage{sender=#1}{tubstypearea}
}
\DeclareOptionX{hyperref}{%
  \PassOptionsToPackage{%
    colorlinks,
    linkcolor=tuRed,
    anchorcolor=tuBlack,
    citecolor=tuGreenDark80,
    filecolor=tuBlue80,
    menucolor=tuRed,
    urlcolor=tuVioletLight
  }{hyperref}
}
\DeclareOptionX{hyperrefdark}{%
  \PassOptionsToPackage{%
    colorlinks,
    linkcolor=tuRed100,
    anchorcolor=tuBlack,
    citecolor=tuGreenDark,
    filecolor=tuBlueDark,
    menucolor=tuRed100,
    urlcolor=tuViolet
  }{hyperref}
}
\DeclareOptionX*{%
  \PassOptionsToClass{\CurrentOption}{\BaseClass}
}
\newcommand\tubs@fontsize{11pt}
\DeclareOptionX{fontsize}{%
  \renewcommand\tubs@fontsize{#1}
}
\newcommand\headingscolor{tuBlack}
\newcommand\tubs@fontcolor[1]{}
\DeclareOptionX{colorheadings}[tuSecondary]{%
  \renewcommand\headingscolor{#1}
  \renewcommand\tubs@fontcolor[1]{\color{#1}}
}
\newif\if@tubs@tf@smallchap\@tubs@tf@smallchapfalse
\DeclareOptionX{smallchapters}{%
  \@tubs@tf@smallchaptrue
}


\newif\if@tp@landscape\@tp@landscapefalse
\newcommand{\tubs@poster@style}{poster}
\DeclareOptionX{style}{%
  % Diese Option erzeugt Formatierung entsprechend der Konventionen für
  % wissenschaftliche Plakate
  \ifthenelse{\equal{#1}{scifi}}{%
    \renewcommand{\tubs@poster@style}{scifi}
    \PassOptionsToPackage{scifiposter}{tubstypearea}
    \PassOptionsToPackage{scifiposter}{tubsstyle}
    % Scifiposter haben eigene Schrift-Definitionen!
    \renewcommand*{\@fsfbs@sub}{scifi}
  }{\ifthenelse{\equal{#1}{bulletin}}{%
    \renewcommand{\tubs@poster@style}{bulletin}
  }{%
    \renewcommand{\tubs@poster@style}{poster}
  }}
}
\DeclareOptionX{landscape}{%
  \@tp@landscapetrue
}
\def\@userlogo{}%
\define@key{tubsposter}{logo}{%
  \gdef\@userlogo{#1}%
}
\PassOptionsToPackage{fullline}{tubsstyle}
\ExecuteOptionsX{a3paper,style=standard,cmyk}
\ProcessOptionsX*\relax

\ifthenelse{\equal{\tubs@poster@style}{scifi}}{%
    \PassOptionsToPackage{scifiposter}{tubslogo}
}{}
\providecommand{\@fontsizefilebase}{}
\renewcommand{\@fontsizefilebase}{\@fsfb@prefix\@fsfbs@sub}
\PassOptionsToClass{DIV=1}{\BaseClass}
\LoadClass{\BaseClass}
\RequirePackage{tubscolors}
\RequirePackage{tubstypearea}
\RequirePackage{tubslogo}
\RequirePackage{tubsstyle}
\RequirePackage{nexus}
\RequirePackage{xcolor}
\colorlet{tubsheadings}{\headingscolor}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand\newtubsfont[3][\relax]{%
  \@ifundefined{scr@fnt@#2}{%
    \newkomafont[#1]{#2}{#3}%
  }{%
    \setkomafont{#2}{#3}%
  }%
}
\newcommand*\addtotubsfont[2]{%
  \@ifundefined{scr@fnt@#1}{}{%
    \addtokomafont{#1}{#2}%
  }%
}
\let\settubsfont\newtubsfont
\let\usetubsfont\usekomafont
\newtubsfont{intro}{}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newtubsfont{absheadline}{\sffamily\bfseries}
\newtubsfont{title}{\usekomafont{absheadline}\Huge}
\newtubsfont{headline}{\usekomafont{title}\tubs@fontcolor{tubsheadings}}
\newtubsfont{headlinesmall}{\usekomafont{absheadline}\huge\tubs@fontcolor{tubsheadings}}
\newtubsfont{subtitle}{\usekomafont{absheadline}\Large}
\newtubsfont{subheadline}{\usekomafont{subtitle}\tubs@fontcolor{tubsheadings}}
\newtubsfont{subheadlinesmall}{\usekomafont{absheadline}\large\tubs@fontcolor{
tubsheadings}}
\newtubsfont{author}{\sffamily\LARGE}
\newtubsfont{date}{\large}
\newtubsfont{institute}{\sffamily\large\bfseries}
\newtubsfont{infotext}{\large}
\newtubsfont{infotextitem}{\large}
\newtubsfont{copytext}{\normalsize}
\newtubsfont{caption}{\small}
\settubsfont{pageheadfoot}{\normalfont\mdseries\scshape}
\settubsfont{pagenumber}{\usekomafont{pagehead}\lnum}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\deffootnotemark{\lnum\textsuperscript{\thefootnotemark}}
\addtotubsfont{footnote}{\lnum}% TODO (see above)
\preto\labelenumi{\lnum}
\preto\labelenumii{\lnum}
\preto\labelenumiii{\lnum}
\providecommand*{\partformat}{\partname~\lnum\thepart\autodot}
\providecommand*\@seccntformat[1]{}%
\providecommand*{\othersectionlevelsformat}[3]{#3\enskip} % HERE!
\renewcommand*\@seccntformat[1]{%
   \protect\othersectionlevelsformat{#1}{%
     \expandafter\aftergroup\noexpand\@gobble}{\protect\lnum\csname the#1\endcsname}%
}
\providecommand*\sectionmarkformat{}%
\renewcommand*\sectionmarkformat{{\protect\lnum\thesection\autodot\enskip}}%
\providecommand*\figureformat{}%
\renewcommand*{\figureformat}{%
  \figurename~\lnum\thefigure%
  \autodot%
}
\providecommand*\tableformat{}%
\renewcommand*{\tableformat}{%
  \tablename~\lnum\thetable%
  \autodot%
}
\providecommand*\numberline@prefix{}%
\renewcommand*{\numberline@prefix}{\lnum}%
\AfterPackage{listings}{%
  \AtBeginDocument{%
    \def\fnum@lstlisting{%
    \lstlistingname
    \ifx\lst@@caption\@empty\else~\lnum\thelstlisting\fi}%
  }%
  \let\@orig@lst@numberstyle\lst@numberstyle
  \lst@AddToHook{Init}{%
    \l@addto@macro\lst@numberstyle\lnum
  }%
}%
\preto\@tabular{\lnum}
\preto\LT@array{\lnum}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newtubsfont{section}{\usekomafont{subheadline}}
\newtubsfont{subsection}{\usekomafont{subheadlinesmall}}
\addtotubsfont{subsubsection}{\tubs@fontcolor{tubsheadings}}
\newtubsfont{intro}{\large\tubs@fontcolor{tubsheadings}}%TODO: mdseries???
\renewcommand{\labelitemi}{\rule[0.1em]{0.4em}{0.4em}}
\renewcommand{\labelitemii}{\rule[0.1em]{0.3em}{0.3em}}
\parindent0mm
\parskip\medskipamount
\newcommand\@sec@cmd[2]{{\raggedsection\usekomafont{#1}#2\par}}
\define@boolkey{sec@cmd}{small}[true]{}%
\let\headline\@undefined
\newcommand\headline[2][]{%
  \setkeys{sec@cmd}{small=false,#1}%
  \ifKV@sec@cmd@small
    \@sec@cmd{headlinesmall}{#2}%
  \else
    \@sec@cmd{headline}{#2}%
  \fi
}
\let\subheadline\@undefined
\newcommand\subheadline[2][]{%
  \setkeys{sec@cmd}{small=false,#1}%
  \ifKV@sec@cmd@small
    \@sec@cmd{subheadlinesmall}{#2}%
  \else
    \@sec@cmd{subheadline}{#2}%
  \fi
}

\RequirePackage{ifthen}
\RequirePackage{xkeyval}
\RequirePackage{tubsbox}
\RequirePackage{tubsstyle}
\newenvironment{tubsposter}{\relax}{\relax}
\newenvironment{posterrow}{\relax}{\relax}
\newenvironment{postercol}{\relax}{\relax}
\newenvironment{postersubrow}{\relax}{\relax}
\ifthenelse{\equal{\tubs@poster@style}{scifi}}{%
  \let\tubsposter=\modulepage
  \let\endtubsposter=\endmodulepage
  \let\posterrow=\modrow
  \let\endposterrow=\endmodrow
  \newenvironment{posterrow*}{\begin{modrow*}}{\end{modrow*}}
  \let\postercol=\modcol
  \let\endpostercol=\endmodcol
  \newenvironment{postercol*}{\begin{modcol*}}{\end{modcol*}}
  \let\postersubrow=\modsubrow
  \let\endpostersubrow=\endmodsubrow
  \newenvironment{postersubrow*}{\begin{modsubrow*}}{\end{modsubrow*}}
}{\ifthenelse{\equal{\tubs@poster@style}{bulletin}}{%
  \renewcommand\tubsposter[1][]{%
    \setkeys{tubsposter}{#1}%
    \gausspage
    \showtubslogo[left]%
    \showlogo{\@userlogo}%
    \showtopline
    \if@tp@landscape
      \segment{6}%
    \else
      \segment{8}%
    \fi
  }
  \def\endtubsposter{%
    \endsegment
    \endgausspage
  }
}{% default
  \let\tubsposter=\gausspage
  \let\endtubsposter=\endgausspage
  \let\posterrow=\segment
  \let\endposterrow=\endsegment
  \def\postercol{\ClassError{tubsposter}{%
    Command is not supported in standard poster style!}{%
    Maybe you should choose another style with option 'style='}%
  }
  \let\endpostercol=\relax
  \def\postersubrow{\ClassError{tubsposter}{%
    Command is not supported in standard poster style!}{%
    Maybe you should choose another style with option 'style='}%
  }
  \let\endpostersubrow=\relax
}}
\endinput
%%
%% End of file `tubsposter.cls'.
